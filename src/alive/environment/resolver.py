"""Deterministic action resolution for ALIVE Version 1.

The resolver is the only Version 1 component allowed to apply action consequences.
It accepts a legal action and an immutable world state, then returns a new state
plus explicit outcome metrics for rewards, debugging, and replay.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from math import isfinite

from .actions import Action, ActionKind
from .models import CommunityState, Resource, ResourceInventory, TechnologyProgress
from .technology import TechnologyEffectKind
from .world import GridWorld, ResourceDeposit, WorldState


@dataclass(frozen=True, slots=True)
class ResolverConfig:
    """Tunable Version 1 transition parameters."""

    base_gather_amount: float = 4.0
    movement_food_cost: float = 0.25
    food_per_person_per_step: float = 0.05
    conserve_food_multiplier: float = 0.75
    population_loss_per_missing_food: float = 0.5
    passive_resource_decay_rate: float = 0.01
    # Version 1.3 population dynamics. All defaults leave Version 1/1.2 unchanged.
    birth_rate_per_step: float = 0.0
    birth_food_cost: float = 1.0
    birth_reserve_per_person: float = 0.5
    natural_death_rate_per_step: float = 0.0
    max_population: float = 120.0
    labor_scales_gathering: bool = False
    max_labor_multiplier: float = 2.0

    @classmethod
    def with_population_dynamics(cls, **overrides) -> "ResolverConfig":
        """Return the Version 1.3 preset: births, deaths, and labour-scaled gathering."""

        values = dict(
            birth_rate_per_step=0.03,
            natural_death_rate_per_step=0.002,
            birth_reserve_per_person=0.2,
            labor_scales_gathering=True,
        )
        values.update(overrides)
        return cls(**values)

    @property
    def population_dynamics_enabled(self) -> bool:
        return (
            self.birth_rate_per_step > 0
            or self.natural_death_rate_per_step > 0
            or self.labor_scales_gathering
        )

    def __post_init__(self) -> None:
        for name in ("birth_rate_per_step", "natural_death_rate_per_step"):
            value = getattr(self, name)
            if not isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if not isfinite(self.max_population) or self.max_population <= 0:
            raise ValueError("max_population must be finite and positive")
        if not isfinite(self.max_labor_multiplier) or self.max_labor_multiplier < 1:
            raise ValueError("max_labor_multiplier must be at least 1")
        non_negative = {
            "birth_food_cost": self.birth_food_cost,
            "birth_reserve_per_person": self.birth_reserve_per_person,
            "base_gather_amount": self.base_gather_amount,
            "movement_food_cost": self.movement_food_cost,
            "food_per_person_per_step": self.food_per_person_per_step,
            "population_loss_per_missing_food": self.population_loss_per_missing_food,
            "passive_resource_decay_rate": self.passive_resource_decay_rate,
        }
        for name, value in non_negative.items():
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if not isfinite(self.conserve_food_multiplier) or not (
            0 < self.conserve_food_multiplier <= 1
        ):
            raise ValueError("conserve_food_multiplier must be greater than 0 and at most 1")
        if self.passive_resource_decay_rate > 1:
            raise ValueError("passive_resource_decay_rate cannot exceed 1")


@dataclass(frozen=True, slots=True)
class StepOutcome:
    """Resolved next state and traceable measurements from one action."""

    action: Action
    next_state: WorldState
    gathered_resource: Resource | None = None
    gathered_amount: float = 0.0
    experiment_technology_id: str | None = None
    discovery_progress_gained: float = 0.0
    technology_completed: str | None = None
    movement_food_spent: float = 0.0
    maintenance_paid: ResourceInventory = field(default_factory=ResourceInventory)
    deactivated_technologies: tuple[str, ...] = ()
    food_consumed: float = 0.0
    food_shortage: float = 0.0
    population_change: float = 0.0
    births: float = 0.0
    starvation_deaths: float = 0.0
    natural_deaths: float = 0.0
    birth_food_spent: float = 0.0
    labor_multiplier: float = 1.0


@dataclass(frozen=True, slots=True)
class ActionResolver:
    """Execute legal actions against a configured :class:`GridWorld`."""

    config: ResolverConfig = field(default_factory=ResolverConfig)

    def resolve(
        self,
        world: GridWorld,
        state: WorldState,
        action: Action,
    ) -> StepOutcome:
        """Resolve one action and advance the world exactly one step."""

        if world.is_terminal(state):
            raise ValueError("cannot resolve an action after the episode has ended")
        if action not in world.legal_actions(state):
            raise ValueError(f"action is illegal in the current state: {action.label}")

        community = state.community
        deposits = state.deposits
        gathered_resource: Resource | None = None
        gathered_amount = 0.0
        experiment_technology_id: str | None = None
        discovery_progress_gained = 0.0
        technology_completed: str | None = None
        movement_food_spent = 0.0
        labor_multiplier = 1.0

        if action.kind is ActionKind.MOVE:
            assert action.direction is not None
            resources, movement_food_spent, movement_shortage = self._consume_food(
                community.resources,
                self.config.movement_food_cost,
            )
            community = replace(
                community,
                position=community.position.shifted(action.direction),
                resources=resources,
            )
        else:
            movement_shortage = 0.0

        if action.kind is ActionKind.GATHER:
            assert action.resource is not None
            deposit = state.deposit_at(community.position, action.resource)
            assert deposit is not None
            gather_multiplier = world.technology_graph.active_multiplier(
                community.technologies,
                TechnologyEffectKind.GATHER_YIELD_MULTIPLIER,
            )
            labor_multiplier = self._labor_multiplier(world, community)
            updated_deposit, gathered_amount = deposit.harvested(
                self.config.base_gather_amount * gather_multiplier * labor_multiplier
            )
            deposits = self._replace_deposit(deposits, updated_deposit)
            community = replace(
                community,
                resources=community.resources.added(action.resource, gathered_amount),
            )
            gathered_resource = action.resource

        if action.kind is ActionKind.EXPERIMENT:
            assert action.technology_id is not None
            (
                community,
                discovery_progress_gained,
                technology_completed,
            ) = self._experiment(world, community, action.technology_id)
            experiment_technology_id = action.technology_id

        (
            community,
            maintenance_paid,
            deactivated_technologies,
        ) = self._apply_technology_maintenance(world, community)

        food_multiplier = world.technology_graph.active_multiplier(
            community.technologies,
            TechnologyEffectKind.FOOD_VALUE_MULTIPLIER,
        )
        conserve_multiplier = (
            self.config.conserve_food_multiplier
            if action.kind is ActionKind.CONSERVE
            else 1.0
        )
        required_food = (
            community.population
            * self.config.food_per_person_per_step
            * conserve_multiplier
            / food_multiplier
        )
        resources, food_consumed, survival_shortage = self._consume_food(
            community.resources,
            required_food,
        )
        total_shortage = movement_shortage + survival_shortage
        starvation_deaths = min(
            community.population,
            total_shortage * self.config.population_loss_per_missing_food,
        )
        natural_deaths = min(
            community.population - starvation_deaths,
            community.population * self.config.natural_death_rate_per_step,
        )
        survivors = community.population - starvation_deaths - natural_deaths
        births, resources, birth_food_spent = self._births(
            survivors, resources, total_shortage
        )
        next_population = survivors + births

        decay_multiplier = world.technology_graph.active_multiplier(
            community.technologies,
            TechnologyEffectKind.RESOURCE_DECAY_MULTIPLIER,
        )
        resources = self._apply_decay(resources, decay_multiplier)
        community = replace(
            community,
            population=next_population,
            available_labor=next_population * world.config.labor_fraction,
            resources=resources,
            previous_action=action.label,
            active=next_population > 0,
        )

        next_state = world.advance_time(
            state,
            community=community,
            deposits=deposits,
        )
        return StepOutcome(
            action=action,
            next_state=next_state,
            gathered_resource=gathered_resource,
            gathered_amount=gathered_amount,
            experiment_technology_id=experiment_technology_id,
            discovery_progress_gained=discovery_progress_gained,
            technology_completed=technology_completed,
            movement_food_spent=movement_food_spent,
            maintenance_paid=maintenance_paid,
            deactivated_technologies=deactivated_technologies,
            food_consumed=food_consumed,
            food_shortage=total_shortage,
            population_change=(
                births - (starvation_deaths + natural_deaths)
                if births
                else -(starvation_deaths + natural_deaths)
            ),
            births=births,
            starvation_deaths=starvation_deaths,
            natural_deaths=natural_deaths,
            birth_food_spent=birth_food_spent,
            labor_multiplier=labor_multiplier,
        )

    def _labor_multiplier(self, world: GridWorld, community: CommunityState) -> float:
        """Scale gathering by available labour relative to the starting workforce."""

        if not self.config.labor_scales_gathering:
            return 1.0
        reference = world.config.starting_population * world.config.labor_fraction
        if reference <= 0:
            return 1.0
        # Diminishing returns (square root): a bigger workforce gathers more, but not
        # proportionally, and a smaller one is not instantly crippled.
        ratio = community.available_labor / reference
        return min(self.config.max_labor_multiplier, ratio ** 0.5)

    def _births(
        self,
        population: float,
        resources: ResourceInventory,
        shortage: float,
    ) -> tuple[float, ResourceInventory, float]:
        """Fed communities grow logistically; each birth costs food."""

        config = self.config
        if config.birth_rate_per_step <= 0 or population <= 0 or shortage > 0:
            return 0.0, resources, 0.0
        room = max(0.0, 1.0 - population / config.max_population)
        desired = population * config.birth_rate_per_step * room
        surplus = resources.food - config.birth_reserve_per_person * population
        if config.birth_food_cost > 0:
            affordable = max(0.0, surplus) / config.birth_food_cost
        else:
            affordable = desired
        births = min(desired, affordable)
        food_spent = births * config.birth_food_cost
        return births, replace(resources, food=resources.food - food_spent), food_spent

    def _experiment(
        self,
        world: GridWorld,
        community: CommunityState,
        technology_id: str,
    ) -> tuple[CommunityState, float, str | None]:
        definition = world.technology_graph.definition(technology_id)
        existing = community.technology(technology_id)
        resources = community.resources

        if existing is None:
            resources = resources.spent(definition.discovery_cost)
            existing = TechnologyProgress(technology_id=technology_id)

        previous_progress = existing.discovery_progress
        next_progress = min(1.0, previous_progress + definition.base_discovery_rate)
        completed = previous_progress < 1.0 and next_progress >= 1.0
        updated = replace(
            existing,
            discovery_progress=next_progress,
            active=next_progress >= 1.0,
        )
        technologies = self._replace_technology(
            community.technologies,
            updated,
            world.technology_graph.topological_ids(),
        )
        return (
            replace(community, resources=resources, technologies=technologies),
            next_progress - previous_progress,
            technology_id if completed else None,
        )

    def _apply_technology_maintenance(
        self,
        world: GridWorld,
        community: CommunityState,
    ) -> tuple[CommunityState, ResourceInventory, tuple[str, ...]]:
        progress_by_id = {
            item.technology_id: item for item in community.technologies
        }
        resources = community.resources
        active_ids: set[str] = set()
        deactivated: list[str] = []
        paid = ResourceInventory()

        for technology_id in world.technology_graph.topological_ids():
            progress = progress_by_id.get(technology_id)
            if progress is None or progress.discovery_progress < 1.0:
                continue

            definition = world.technology_graph.definition(technology_id)
            prerequisites_active = definition.prerequisites <= active_ids
            can_maintain = resources.can_afford(definition.maintenance_cost)
            should_be_active = prerequisites_active and can_maintain

            if should_be_active:
                resources = resources.spent(definition.maintenance_cost)
                paid = ResourceInventory(
                    food=paid.food + definition.maintenance_cost.food,
                    wood=paid.wood + definition.maintenance_cost.wood,
                    stone=paid.stone + definition.maintenance_cost.stone,
                )
                active_ids.add(technology_id)
            elif progress.active:
                deactivated.append(technology_id)

            progress_by_id[technology_id] = replace(
                progress,
                active=should_be_active,
            )

        ordered_progress = tuple(
            progress_by_id[technology_id]
            for technology_id in world.technology_graph.topological_ids()
            if technology_id in progress_by_id
        )
        return (
            replace(community, resources=resources, technologies=ordered_progress),
            paid,
            tuple(deactivated),
        )

    def _apply_decay(
        self,
        resources: ResourceInventory,
        technology_multiplier: float,
    ) -> ResourceInventory:
        retained_fraction = max(
            0.0,
            1.0 - self.config.passive_resource_decay_rate * technology_multiplier,
        )
        return ResourceInventory(
            food=resources.food * retained_fraction,
            wood=resources.wood * retained_fraction,
            stone=resources.stone * retained_fraction,
        )

    @staticmethod
    def _consume_food(
        resources: ResourceInventory,
        requested: float,
    ) -> tuple[ResourceInventory, float, float]:
        consumed = min(resources.food, requested)
        shortage = requested - consumed
        return (
            replace(resources, food=resources.food - consumed),
            consumed,
            shortage,
        )

    @staticmethod
    def _replace_deposit(
        deposits: tuple[ResourceDeposit, ...],
        replacement: ResourceDeposit,
    ) -> tuple[ResourceDeposit, ...]:
        return tuple(
            replacement if deposit.key == replacement.key else deposit
            for deposit in deposits
        )

    @staticmethod
    def _replace_technology(
        technologies: tuple[TechnologyProgress, ...],
        replacement: TechnologyProgress,
        graph_order: tuple[str, ...],
    ) -> tuple[TechnologyProgress, ...]:
        by_id = {item.technology_id: item for item in technologies}
        by_id[replacement.technology_id] = replacement
        return tuple(
            by_id[technology_id]
            for technology_id in graph_order
            if technology_id in by_id
        )
