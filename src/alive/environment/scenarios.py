"""Seeded reference scenarios for ALIVE Version 1.

Scenarios configure and initialize the generic simulation engine; they do not
change its rules. The built-in stable and scarcity presets are reproducible
development fixtures whose numeric values can later move to external YAML files
without changing the world, action, or resolver APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from random import Random
from typing import Callable

from .models import Position, Resource, ResourceInventory, WorldConfig
from .technology import TechnologyGraph, starter_technology_graph
from .world import GridWorld, ResourceDeposit, WorldState


@dataclass(frozen=True, slots=True)
class DepositDistribution:
    """Generation ranges for deposits of one resource type."""

    resource: Resource
    count: int
    capacity_min: float
    capacity_max: float
    initial_fill_min: float
    initial_fill_max: float
    regeneration_min: float
    regeneration_max: float

    def __post_init__(self) -> None:
        if self.count <= 0:
            raise ValueError("deposit count must be positive")
        self._validate_range("capacity", self.capacity_min, self.capacity_max)
        self._validate_range(
            "initial_fill",
            self.initial_fill_min,
            self.initial_fill_max,
            minimum=0.0,
            maximum=1.0,
        )
        self._validate_range(
            "regeneration",
            self.regeneration_min,
            self.regeneration_max,
            minimum=0.0,
        )
        if self.capacity_min <= 0:
            raise ValueError("deposit capacity must be positive")

    @staticmethod
    def _validate_range(
        name: str,
        lower: float,
        upper: float,
        *,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        if not isfinite(lower) or not isfinite(upper):
            raise ValueError(f"{name} range must contain finite values")
        if lower > upper:
            raise ValueError(f"{name} minimum cannot exceed its maximum")
        if minimum is not None and lower < minimum:
            raise ValueError(f"{name} minimum cannot be below {minimum}")
        if maximum is not None and upper > maximum:
            raise ValueError(f"{name} maximum cannot exceed {maximum}")


@dataclass(frozen=True, slots=True)
class ScenarioInstance:
    """A generated world and initial state ready to run."""

    scenario_name: str
    description: str
    seed: int
    world: GridWorld
    initial_state: WorldState


@dataclass(frozen=True, slots=True)
class ScenarioDefinition:
    """Validated, seedable recipe for a family of Version 1 worlds."""

    name: str
    description: str
    world_config: WorldConfig
    deposits: tuple[DepositDistribution, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("scenario name cannot be empty")
        if not self.description.strip():
            raise ValueError("scenario description cannot be empty")
        if not self.deposits:
            raise ValueError("scenario must define resource deposits")

        resources = [distribution.resource for distribution in self.deposits]
        if len(resources) != len(set(resources)):
            raise ValueError("scenario can define each resource distribution only once")
        if set(resources) != set(Resource):
            raise ValueError("Version 1 scenarios must configure food, wood, and stone")

        cell_count = self.world_config.width * self.world_config.height
        for distribution in self.deposits:
            if distribution.count > cell_count:
                raise ValueError(
                    f"{distribution.resource.value} deposit count exceeds map cells"
                )

    @property
    def community_start(self) -> Position:
        """Return the deterministic central starting cell."""

        return Position(
            self.world_config.width // 2,
            self.world_config.height // 2,
        )

    def generate(
        self,
        seed: int,
        *,
        technology_graph: TechnologyGraph | None = None,
    ) -> ScenarioInstance:
        """Generate a reproducible world instance from ``seed``."""

        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError("scenario seed must be an integer")

        graph = technology_graph or starter_technology_graph()
        world = GridWorld(self.world_config, graph)
        random = Random(seed)
        generated_deposits: list[ResourceDeposit] = []

        for distribution in self.deposits:
            used_positions: set[Position] = set()
            anchor = self._anchor_for(distribution.resource)
            positions = [anchor]
            used_positions.add(anchor)

            while len(positions) < distribution.count:
                candidate = Position(
                    random.randrange(self.world_config.width),
                    random.randrange(self.world_config.height),
                )
                if candidate not in used_positions:
                    positions.append(candidate)
                    used_positions.add(candidate)

            for position in positions:
                capacity = random.uniform(
                    distribution.capacity_min,
                    distribution.capacity_max,
                )
                fill = random.uniform(
                    distribution.initial_fill_min,
                    distribution.initial_fill_max,
                )
                regeneration = random.uniform(
                    distribution.regeneration_min,
                    distribution.regeneration_max,
                )
                generated_deposits.append(
                    ResourceDeposit(
                        position=position,
                        resource=distribution.resource,
                        amount=round(capacity * fill, 4),
                        capacity=round(capacity, 4),
                        regeneration_per_step=round(regeneration, 4),
                    )
                )

        initial_state = world.initial_state(
            community_position=self.community_start,
            deposits=generated_deposits,
            episode_seed=seed,
        )
        return ScenarioInstance(
            scenario_name=self.name,
            description=self.description,
            seed=seed,
            world=world,
            initial_state=initial_state,
        )

    def _anchor_for(self, resource: Resource) -> Position:
        """Guarantee that every starting observation contains all resources."""

        start = self.community_start
        return {
            Resource.FOOD: start,
            Resource.WOOD: Position(start.x + 1, start.y),
            Resource.STONE: Position(start.x, start.y + 1),
        }[resource]


def stable_scenario() -> ScenarioDefinition:
    """Return the initial abundant environment used to verify basic learning."""

    return ScenarioDefinition(
        name="stable",
        description=(
            "An abundant world with broad resource coverage and forgiving "
            "regeneration for initial agent training."
        ),
        world_config=WorldConfig(
            width=16,
            height=16,
            max_steps=256,
            observation_radius=2,
            starting_population=40.0,
            labor_fraction=0.6,
            starting_resources=ResourceInventory(food=30.0, wood=10.0, stone=5.0),
        ),
        deposits=(
            DepositDistribution(Resource.FOOD, 18, 18.0, 30.0, 0.65, 1.0, 0.40, 0.80),
            DepositDistribution(Resource.WOOD, 12, 14.0, 24.0, 0.60, 1.0, 0.20, 0.50),
            DepositDistribution(Resource.STONE, 10, 12.0, 22.0, 0.55, 0.90, 0.08, 0.25),
        ),
    )


def scarcity_scenario() -> ScenarioDefinition:
    """Return a lower-resource environment used to test adaptation."""

    return ScenarioDefinition(
        name="scarcity",
        description=(
            "A sparse world with smaller deposits, slower regeneration, and "
            "lower starting reserves."
        ),
        world_config=WorldConfig(
            width=16,
            height=16,
            max_steps=256,
            observation_radius=2,
            starting_population=40.0,
            labor_fraction=0.6,
            starting_resources=ResourceInventory(food=18.0, wood=7.0, stone=4.0),
        ),
        deposits=(
            DepositDistribution(Resource.FOOD, 10, 10.0, 18.0, 0.45, 0.75, 0.15, 0.35),
            DepositDistribution(Resource.WOOD, 7, 8.0, 15.0, 0.40, 0.70, 0.08, 0.22),
            DepositDistribution(Resource.STONE, 5, 7.0, 13.0, 0.35, 0.65, 0.02, 0.10),
        ),
    )


_SCENARIO_FACTORIES: dict[str, Callable[[], ScenarioDefinition]] = {
    "stable": stable_scenario,
    "scarcity": scarcity_scenario,
}


def available_scenarios() -> tuple[str, ...]:
    """Return registered built-in scenario names."""

    return tuple(_SCENARIO_FACTORIES)


def scenario_by_name(name: str) -> ScenarioDefinition:
    """Return a fresh built-in scenario definition by name."""

    normalized_name = name.strip().lower()
    try:
        return _SCENARIO_FACTORIES[normalized_name]()
    except KeyError as error:
        choices = ", ".join(available_scenarios())
        raise KeyError(f"unknown scenario {name!r}; available scenarios: {choices}") from error
