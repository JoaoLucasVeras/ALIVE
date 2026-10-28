"""Core domain models for the first ALIVE simulation level.

This module deliberately contains no reinforcement-learning or rendering code.
It defines the small, validated vocabulary that the world engine, baseline
agents, training code, and replay tools will share.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from math import isfinite
from typing import Iterable


class Resource(StrEnum):
    """Resource categories available in the Version 1 world."""

    FOOD = "food"
    WOOD = "wood"
    STONE = "stone"


class Direction(StrEnum):
    """Cardinal movement choices available to a community."""

    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    @property
    def delta(self) -> tuple[int, int]:
        """Return the ``(x, y)`` offset associated with this direction."""

        return {
            Direction.NORTH: (0, -1),
            Direction.SOUTH: (0, 1),
            Direction.EAST: (1, 0),
            Direction.WEST: (-1, 0),
        }[self]


@dataclass(frozen=True, slots=True, order=True)
class Position:
    """An immutable coordinate in the grid world."""

    x: int
    y: int

    def shifted(self, direction: Direction) -> Position:
        """Return the adjacent position without applying world boundaries."""

        dx, dy = direction.delta
        return Position(self.x + dx, self.y + dy)

    def manhattan_distance(self, other: Position) -> int:
        """Return grid travel distance when diagonal movement is unavailable."""

        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass(frozen=True, slots=True)
class ResourceInventory:
    """A fixed-shape resource inventory.

    Named fields prevent misspelled resource keys and guarantee a stable order
    when this state is eventually converted into an RL observation vector.
    """

    food: float = 0.0
    wood: float = 0.0
    stone: float = 0.0

    def __post_init__(self) -> None:
        for resource in Resource:
            amount = self.amount(resource)
            if not isfinite(amount) or amount < 0:
                raise ValueError(
                    f"{resource.value} must be a finite non-negative amount; "
                    f"received {amount!r}"
                )

    def amount(self, resource: Resource) -> float:
        """Return the amount stored for ``resource``."""

        return float(getattr(self, resource.value))

    def can_afford(self, cost: ResourceInventory) -> bool:
        """Return whether every component of ``cost`` is available."""

        return all(self.amount(item) >= cost.amount(item) for item in Resource)

    def added(self, resource: Resource, amount: float) -> ResourceInventory:
        """Return a new inventory after adding a non-negative amount."""

        if not isfinite(amount) or amount < 0:
            raise ValueError("added amount must be finite and non-negative")
        return replace(self, **{resource.value: self.amount(resource) + amount})

    def spent(self, cost: ResourceInventory) -> ResourceInventory:
        """Return a new inventory after paying ``cost``.

        Raises:
            ValueError: If the inventory cannot afford the requested cost.
        """

        if not self.can_afford(cost):
            raise ValueError("inventory cannot afford the requested cost")
        return ResourceInventory(
            food=self.food - cost.food,
            wood=self.wood - cost.wood,
            stone=self.stone - cost.stone,
        )

    def as_tuple(self) -> tuple[float, float, float]:
        """Return values in the stable ``food, wood, stone`` order."""

        return self.food, self.wood, self.stone


@dataclass(frozen=True, slots=True)
class TechnologyProgress:
    """One community's progress and proficiency for a technology node."""

    technology_id: str
    discovery_progress: float = 0.0
    proficiency: float = 0.0
    active: bool = False

    def __post_init__(self) -> None:
        if not self.technology_id.strip():
            raise ValueError("technology_id cannot be empty")
        for name, value in (
            ("discovery_progress", self.discovery_progress),
            ("proficiency", self.proficiency),
        ):
            if not isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")
        if self.active and self.discovery_progress < 1.0:
            raise ValueError("an active technology must be fully discovered")


@dataclass(frozen=True, slots=True)
class CommunityState:
    """Complete engine-owned state for the single Version 1 community."""

    community_id: str
    position: Position
    population: float
    available_labor: float
    resources: ResourceInventory = field(default_factory=ResourceInventory)
    technologies: tuple[TechnologyProgress, ...] = ()
    previous_action: str | None = None
    active: bool = True

    def __post_init__(self) -> None:
        if not self.community_id.strip():
            raise ValueError("community_id cannot be empty")
        if not isfinite(self.population) or self.population < 0:
            raise ValueError("population must be finite and non-negative")
        if not isfinite(self.available_labor) or self.available_labor < 0:
            raise ValueError("available_labor must be finite and non-negative")
        if self.available_labor > self.population:
            raise ValueError("available_labor cannot exceed population")
        if self.active != (self.population > 0):
            raise ValueError("active must be true exactly when population is positive")

        technology_ids = [item.technology_id for item in self.technologies]
        if len(technology_ids) != len(set(technology_ids)):
            raise ValueError("technology entries must have unique IDs")

    def technology(self, technology_id: str) -> TechnologyProgress | None:
        """Return progress for a technology, or ``None`` if it is unknown."""

        return next(
            (item for item in self.technologies if item.technology_id == technology_id),
            None,
        )


@dataclass(frozen=True, slots=True)
class WorldConfig:
    """Validated dimensions and starting values for a Version 1 episode."""

    width: int = 16
    height: int = 16
    max_steps: int = 256
    observation_radius: int = 2
    starting_population: float = 40.0
    labor_fraction: float = 0.6
    starting_resources: ResourceInventory = field(
        default_factory=lambda: ResourceInventory(food=30.0, wood=10.0, stone=5.0)
    )

    def __post_init__(self) -> None:
        if self.width < 4 or self.height < 4:
            raise ValueError("world dimensions must each be at least 4 cells")
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
        if self.observation_radius < 0:
            raise ValueError("observation_radius cannot be negative")
        if self.observation_radius >= max(self.width, self.height):
            raise ValueError("observation_radius must be smaller than the world")
        if not isfinite(self.starting_population) or self.starting_population <= 0:
            raise ValueError("starting_population must be finite and positive")
        if not isfinite(self.labor_fraction) or not 0.0 <= self.labor_fraction <= 1.0:
            raise ValueError("labor_fraction must be between 0.0 and 1.0")

    def contains(self, position: Position) -> bool:
        """Return whether ``position`` lies within the configured grid."""

        return 0 <= position.x < self.width and 0 <= position.y < self.height

    def initial_community(
        self,
        position: Position,
        *,
        community_id: str = "community-0",
        technologies: Iterable[TechnologyProgress] = (),
    ) -> CommunityState:
        """Construct the validated initial community for an episode."""

        if not self.contains(position):
            raise ValueError("initial community position is outside the world")
        return CommunityState(
            community_id=community_id,
            position=position,
            population=self.starting_population,
            available_labor=self.starting_population * self.labor_fraction,
            resources=self.starting_resources,
            technologies=tuple(technologies),
        )
