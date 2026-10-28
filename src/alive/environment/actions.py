"""Action vocabulary and discrete encoding for ALIVE Version 1.

Every controller uses these same action objects. Random and rule-based agents
can work with their readable form, while reinforcement-learning policies use the
stable integer indices supplied by :class:`ActionCatalog`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Iterable

from .models import Direction, Resource
from .technology import TechnologyGraph


class ActionKind(StrEnum):
    """Action families available to the first-level community."""

    MOVE = "move"
    GATHER = "gather"
    EXPERIMENT = "experiment"
    CONSERVE = "conserve"


@dataclass(frozen=True, slots=True)
class Action:
    """One fully specified community action.

    Each action family accepts exactly one parameter shape:

    - ``MOVE`` requires ``direction``.
    - ``GATHER`` requires ``resource``.
    - ``EXPERIMENT`` requires ``technology_id``.
    - ``CONSERVE`` has no parameter.
    """

    kind: ActionKind
    direction: Direction | None = None
    resource: Resource | None = None
    technology_id: str | None = None

    def __post_init__(self) -> None:
        required_fields = {
            ActionKind.MOVE: {"direction"},
            ActionKind.GATHER: {"resource"},
            ActionKind.EXPERIMENT: {"technology_id"},
            ActionKind.CONSERVE: set(),
        }[self.kind]
        populated_fields = {
            name
            for name, value in (
                ("direction", self.direction),
                ("resource", self.resource),
                ("technology_id", self.technology_id),
            )
            if value is not None
        }
        if populated_fields != required_fields:
            expected = ", ".join(sorted(required_fields)) or "no parameters"
            received = ", ".join(sorted(populated_fields)) or "no parameters"
            raise ValueError(
                f"{self.kind.value} requires {expected}; received {received}"
            )
        if self.technology_id is not None and not self.technology_id.strip():
            raise ValueError("technology_id cannot be blank")

    @classmethod
    def move(cls, direction: Direction) -> Action:
        """Construct a movement action."""

        return cls(ActionKind.MOVE, direction=direction)

    @classmethod
    def gather(cls, resource: Resource) -> Action:
        """Construct a resource-gathering action."""

        return cls(ActionKind.GATHER, resource=resource)

    @classmethod
    def experiment(cls, technology_id: str) -> Action:
        """Construct a technology-experiment action."""

        return cls(ActionKind.EXPERIMENT, technology_id=technology_id)

    @classmethod
    def conserve(cls) -> Action:
        """Construct the always-available low-activity action."""

        return cls(ActionKind.CONSERVE)

    @property
    def label(self) -> str:
        """Return a stable human-readable label for logs and visualizations."""

        if self.direction is not None:
            return f"move:{self.direction.value}"
        if self.resource is not None:
            return f"gather:{self.resource.value}"
        if self.technology_id is not None:
            return f"experiment:{self.technology_id}"
        return self.kind.value


@dataclass(frozen=True, slots=True)
class ActionMask:
    """Boolean legality values aligned with an :class:`ActionCatalog`."""

    values: tuple[bool, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError("action mask cannot be empty")
        if not any(self.values):
            raise ValueError("action mask must leave at least one legal action")

    def is_legal(self, index: int) -> bool:
        """Return whether an encoded action index is legal."""

        if not 0 <= index < len(self.values):
            raise IndexError(f"action index {index} is outside the mask")
        return self.values[index]

    @property
    def legal_indices(self) -> tuple[int, ...]:
        """Return every legal encoded action index."""

        return tuple(index for index, legal in enumerate(self.values) if legal)


@dataclass(frozen=True, slots=True)
class ActionCatalog:
    """Stable bidirectional mapping between actions and policy indices."""

    actions: tuple[Action, ...]

    def __post_init__(self) -> None:
        if not self.actions:
            raise ValueError("action catalog cannot be empty")
        if len(self.actions) != len(set(self.actions)):
            raise ValueError("action catalog cannot contain duplicates")
        if Action.conserve() not in self.actions:
            raise ValueError("action catalog must include conserve as a safe fallback")

    @classmethod
    def for_graph(cls, graph: TechnologyGraph) -> ActionCatalog:
        """Build the canonical Version 1 catalog for a technology graph.

        Ordering is part of the model interface and must not change without an
        explicit compatibility migration.
        """

        actions = (
            *(Action.move(direction) for direction in Direction),
            *(Action.gather(resource) for resource in Resource),
            *(
                Action.experiment(technology_id)
                for technology_id in graph.topological_ids()
            ),
            Action.conserve(),
        )
        return cls(tuple(actions))

    def encode(self, action: Action) -> int:
        """Return the stable policy index for ``action``."""

        try:
            return self.actions.index(action)
        except ValueError as error:
            raise KeyError(f"action is not in this catalog: {action.label}") from error

    def decode(self, index: int) -> Action:
        """Return the readable action represented by a policy index."""

        if not 0 <= index < len(self.actions):
            raise IndexError(f"action index {index} is outside the catalog")
        return self.actions[index]

    def mask_from_legal_actions(self, legal_actions: Iterable[Action]) -> ActionMask:
        """Create a mask from actions already validated by the world engine."""

        legal_set = set(legal_actions)
        unknown = legal_set - set(self.actions)
        if unknown:
            labels = ", ".join(sorted(action.label for action in unknown))
            raise ValueError(f"legal action collection contains unknown actions: {labels}")
        return ActionMask(tuple(action in legal_set for action in self.actions))

    def mask_from_predicate(self, is_legal: Callable[[Action], bool]) -> ActionMask:
        """Evaluate an engine legality function for every catalog action."""

        return ActionMask(tuple(bool(is_legal(action)) for action in self.actions))

    def require_legal(self, index: int, mask: ActionMask) -> Action:
        """Decode an index only when its aligned mask marks it as legal."""

        if len(mask.values) != len(self.actions):
            raise ValueError("action mask length does not match the catalog")
        if not mask.is_legal(index):
            raise ValueError(f"action is illegal in the current state: {self.decode(index).label}")
        return self.decode(index)

    @property
    def labels(self) -> tuple[str, ...]:
        """Return labels in policy-index order."""

        return tuple(action.label for action in self.actions)
