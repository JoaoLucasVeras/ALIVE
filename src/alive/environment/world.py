"""Grid-world state and legality rules for ALIVE Version 1.

This module owns spatial facts and passive world behavior. It knows where the
community and resource deposits are, what the community can currently see, how
resources regenerate, and which configured actions are legal. Action outcomes
such as movement costs, gathering yields, and discovery progress belong in the
separate resolver that will consume this world API.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from math import isfinite
from typing import Iterable

from .actions import Action, ActionCatalog, ActionKind, ActionMask
from .models import (
    CommunityState,
    Position,
    Resource,
    TechnologyProgress,
    WorldConfig,
)
from .technology import TechnologyGraph


@dataclass(frozen=True, slots=True)
class ResourceDeposit:
    """A renewable quantity of one resource at one grid position."""

    position: Position
    resource: Resource
    amount: float
    capacity: float
    regeneration_per_step: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("amount", self.amount),
            ("capacity", self.capacity),
            ("regeneration_per_step", self.regeneration_per_step),
        ):
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if self.capacity <= 0:
            raise ValueError("resource deposit capacity must be positive")
        if self.amount > self.capacity:
            raise ValueError("resource deposit amount cannot exceed capacity")

    @property
    def key(self) -> tuple[Position, Resource]:
        """Return the identity used to prevent duplicate deposits."""

        return self.position, self.resource

    def regenerated(self) -> ResourceDeposit:
        """Return the deposit after one passive regeneration step."""

        return replace(
            self,
            amount=min(self.capacity, self.amount + self.regeneration_per_step),
        )

    def harvested(self, requested_amount: float) -> tuple[ResourceDeposit, float]:
        """Remove up to ``requested_amount`` and return deposit plus actual yield."""

        if not isfinite(requested_amount) or requested_amount < 0:
            raise ValueError("requested harvest must be finite and non-negative")
        harvested_amount = min(self.amount, requested_amount)
        return replace(self, amount=self.amount - harvested_amount), harvested_amount


@dataclass(frozen=True, slots=True)
class WorldState:
    """Complete replayable state for one point in a Version 1 episode."""

    step: int
    episode_seed: int
    community: CommunityState
    deposits: tuple[ResourceDeposit, ...]

    def deposit_at(
        self,
        position: Position,
        resource: Resource,
    ) -> ResourceDeposit | None:
        """Return a matching deposit, or ``None`` when the cell lacks it."""

        return next(
            (
                deposit
                for deposit in self.deposits
                if deposit.position == position and deposit.resource is resource
            ),
            None,
        )


@dataclass(frozen=True, slots=True)
class GridWorld:
    """Validated Version 1 world definition and passive transition rules."""

    config: WorldConfig
    technology_graph: TechnologyGraph
    action_catalog: ActionCatalog = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "action_catalog",
            ActionCatalog.for_graph(self.technology_graph),
        )

    def initial_state(
        self,
        *,
        community_position: Position,
        deposits: Iterable[ResourceDeposit],
        episode_seed: int,
        technologies: Iterable[TechnologyProgress] = (),
        community_id: str = "community-0",
    ) -> WorldState:
        """Construct and validate the initial state of a seeded episode."""

        community = self.config.initial_community(
            community_position,
            community_id=community_id,
            technologies=technologies,
        )
        state = WorldState(
            step=0,
            episode_seed=episode_seed,
            community=community,
            deposits=self._ordered_deposits(deposits),
        )
        self.validate_state(state)
        return state

    def _ordered_deposits(
        self,
        deposits: Iterable[ResourceDeposit],
    ) -> tuple[ResourceDeposit, ...]:
        """Return deposits in deterministic observation and replay order."""

        return tuple(
            sorted(
                deposits,
                key=lambda item: (
                    item.position.y,
                    item.position.x,
                    item.resource.value,
                ),
            )
        )

    def validate_state(self, state: WorldState) -> None:
        """Reject world states that violate spatial or episode invariants."""

        if state.step < 0:
            raise ValueError("world step cannot be negative")
        if state.step > self.config.max_steps:
            raise ValueError("world step cannot exceed the episode limit")
        if not self.config.contains(state.community.position):
            raise ValueError("community position is outside the world")

        deposit_keys: set[tuple[Position, Resource]] = set()
        for deposit in state.deposits:
            if not self.config.contains(deposit.position):
                raise ValueError(
                    f"{deposit.resource.value} deposit at {deposit.position} is outside the world"
                )
            if deposit.key in deposit_keys:
                raise ValueError(
                    "a cell can contain at most one deposit of each resource type"
                )
            deposit_keys.add(deposit.key)

        graph_ids = {item.technology_id for item in self.technology_graph.technologies}
        unknown_technologies = {
            item.technology_id for item in state.community.technologies
        } - graph_ids
        if unknown_technologies:
            names = ", ".join(sorted(unknown_technologies))
            raise ValueError(f"community state contains unknown technologies: {names}")

    def visible_deposits(self, state: WorldState) -> tuple[ResourceDeposit, ...]:
        """Return deposits within the community's Manhattan observation radius."""

        self.validate_state(state)
        origin = state.community.position
        return tuple(
            deposit
            for deposit in state.deposits
            if origin.manhattan_distance(deposit.position)
            <= self.config.observation_radius
        )

    def legal_actions(self, state: WorldState) -> tuple[Action, ...]:
        """Return legal actions in stable policy-index order."""

        self.validate_state(state)
        if self.is_terminal(state):
            return (Action.conserve(),)

        discoverable = set(
            self.technology_graph.discoverable_ids(state.community.technologies)
        )
        legal: list[Action] = []

        for action in self.action_catalog.actions:
            if action.kind is ActionKind.CONSERVE:
                legal.append(action)
                continue

            if action.kind is ActionKind.MOVE:
                assert action.direction is not None
                if self.config.contains(state.community.position.shifted(action.direction)):
                    legal.append(action)
                continue

            if action.kind is ActionKind.GATHER:
                assert action.resource is not None
                deposit = state.deposit_at(state.community.position, action.resource)
                if (
                    deposit is not None
                    and deposit.amount > 0
                    and state.community.available_labor > 0
                ):
                    legal.append(action)
                continue

            if action.kind is ActionKind.EXPERIMENT:
                assert action.technology_id is not None
                technology = self.technology_graph.definition(action.technology_id)
                existing_progress = state.community.technology(action.technology_id)
                can_fund_research = (
                    existing_progress is not None
                    or state.community.resources.can_afford(technology.discovery_cost)
                )
                if (
                    action.technology_id in discoverable
                    and state.community.available_labor >= technology.discovery_labor
                    and can_fund_research
                ):
                    legal.append(action)

        return tuple(legal)

    def legal_action_mask(self, state: WorldState) -> ActionMask:
        """Return the policy-aligned legality mask for ``state``."""

        return self.action_catalog.mask_from_legal_actions(self.legal_actions(state))

    def advance_time(
        self,
        state: WorldState,
        *,
        community: CommunityState | None = None,
        deposits: Iterable[ResourceDeposit] | None = None,
    ) -> WorldState:
        """Advance one step and apply passive resource regeneration.

        The future action resolver will supply the post-action community and
        deposits. Regeneration then occurs exactly once at this boundary.
        """

        self.validate_state(state)
        if self.is_terminal(state):
            raise ValueError("cannot advance a completed episode")

        post_action_deposits = (
            state.deposits if deposits is None else self._ordered_deposits(deposits)
        )
        next_state = WorldState(
            step=state.step + 1,
            episode_seed=state.episode_seed,
            community=state.community if community is None else community,
            deposits=tuple(deposit.regenerated() for deposit in post_action_deposits),
        )
        self.validate_state(next_state)
        return next_state

    def is_terminal(self, state: WorldState) -> bool:
        """Return whether population collapse or the step limit ended the episode."""

        return not state.community.active or state.step >= self.config.max_steps
