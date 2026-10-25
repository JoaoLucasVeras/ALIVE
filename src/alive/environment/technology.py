"""Technology definitions and graph rules for ALIVE Level 1.

The technology layer describes what can be discovered and which numeric world
effects become active afterward. It does not decide what a community should
research; random, rule-based, and reinforcement-learning agents will all make
that choice through the same action interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite, prod
import re
from typing import Iterable

from .models import ResourceInventory, TechnologyProgress


_TECHNOLOGY_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class TechnologyEffectKind(StrEnum):
    """Numeric effects supported by the first simulation level."""

    GATHER_YIELD_MULTIPLIER = "gather_yield_multiplier"
    FOOD_VALUE_MULTIPLIER = "food_value_multiplier"
    RESOURCE_DECAY_MULTIPLIER = "resource_decay_multiplier"


@dataclass(frozen=True, slots=True)
class TechnologyEffect:
    """A multiplicative modifier contributed by an active technology."""

    kind: TechnologyEffectKind
    multiplier: float

    def __post_init__(self) -> None:
        if not isfinite(self.multiplier) or self.multiplier <= 0:
            raise ValueError("technology effect multipliers must be finite and positive")


@dataclass(frozen=True, slots=True)
class TechnologyDefinition:
    """Static, versionable configuration for one technology node."""

    technology_id: str
    name: str
    description: str
    prerequisites: frozenset[str] = frozenset()
    discovery_cost: ResourceInventory = ResourceInventory()
    maintenance_cost: ResourceInventory = ResourceInventory()
    discovery_labor: float = 0.0
    base_discovery_rate: float = 0.1
    effects: tuple[TechnologyEffect, ...] = ()

    def __post_init__(self) -> None:
        if not _TECHNOLOGY_ID_PATTERN.fullmatch(self.technology_id):
            raise ValueError(
                "technology_id must start with a lowercase letter and contain "
                "only lowercase letters, numbers, or underscores"
            )
        if not self.name.strip():
            raise ValueError("technology name cannot be empty")
        if not self.description.strip():
            raise ValueError("technology description cannot be empty")
        if self.technology_id in self.prerequisites:
            raise ValueError("a technology cannot require itself")
        if not isfinite(self.discovery_labor) or self.discovery_labor < 0:
            raise ValueError("discovery_labor must be finite and non-negative")
        if not isfinite(self.base_discovery_rate) or not 0 < self.base_discovery_rate <= 1:
            raise ValueError("base_discovery_rate must be greater than 0 and at most 1")

        effect_kinds = [effect.kind for effect in self.effects]
        if len(effect_kinds) != len(set(effect_kinds)):
            raise ValueError("a technology can define each effect kind only once")

    def effect_multiplier(self, kind: TechnologyEffectKind) -> float:
        """Return this node's multiplier for ``kind``, defaulting to neutral."""

        effect = next((item for item in self.effects if item.kind is kind), None)
        return effect.multiplier if effect is not None else 1.0


@dataclass(frozen=True, slots=True)
class TechnologyGraph:
    """An immutable, validated directed acyclic technology graph."""

    technologies: tuple[TechnologyDefinition, ...]

    def __post_init__(self) -> None:
        if not self.technologies:
            raise ValueError("technology graph must contain at least one node")

        identifiers = [item.technology_id for item in self.technologies]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("technology graph IDs must be unique")

        known_ids = set(identifiers)
        for technology in self.technologies:
            missing = technology.prerequisites - known_ids
            if missing:
                names = ", ".join(sorted(missing))
                raise ValueError(
                    f"technology {technology.technology_id!r} has unknown "
                    f"prerequisites: {names}"
                )

        self._validate_acyclic()

    def _validate_acyclic(self) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(technology_id: str) -> None:
            if technology_id in visiting:
                raise ValueError("technology graph cannot contain prerequisite cycles")
            if technology_id in visited:
                return

            visiting.add(technology_id)
            for prerequisite in self.definition(technology_id).prerequisites:
                visit(prerequisite)
            visiting.remove(technology_id)
            visited.add(technology_id)

        for technology in self.technologies:
            visit(technology.technology_id)

    def definition(self, technology_id: str) -> TechnologyDefinition:
        """Return a technology definition or raise a descriptive error."""

        technology = next(
            (item for item in self.technologies if item.technology_id == technology_id),
            None,
        )
        if technology is None:
            raise KeyError(f"unknown technology: {technology_id}")
        return technology

    def topological_ids(self) -> tuple[str, ...]:
        """Return IDs with every prerequisite before its dependents."""

        ordered: list[str] = []
        visited: set[str] = set()

        def append_with_prerequisites(technology_id: str) -> None:
            if technology_id in visited:
                return
            for prerequisite in sorted(self.definition(technology_id).prerequisites):
                append_with_prerequisites(prerequisite)
            visited.add(technology_id)
            ordered.append(technology_id)

        for technology in self.technologies:
            append_with_prerequisites(technology.technology_id)
        return tuple(ordered)

    def discoverable_ids(
        self,
        progress: Iterable[TechnologyProgress],
    ) -> tuple[str, ...]:
        """Return undiscovered nodes whose prerequisites are fully discovered."""

        progress_by_id = {item.technology_id: item for item in progress}
        unknown_progress = progress_by_id.keys() - {
            item.technology_id for item in self.technologies
        }
        if unknown_progress:
            names = ", ".join(sorted(unknown_progress))
            raise ValueError(f"progress contains technologies outside this graph: {names}")

        discovered = {
            technology_id
            for technology_id, item in progress_by_id.items()
            if item.discovery_progress >= 1.0
        }
        return tuple(
            technology_id
            for technology_id in self.topological_ids()
            if technology_id not in discovered
            and self.definition(technology_id).prerequisites <= discovered
        )

    def active_multiplier(
        self,
        progress: Iterable[TechnologyProgress],
        kind: TechnologyEffectKind,
    ) -> float:
        """Combine active effects of ``kind`` multiplicatively."""

        active_ids = {item.technology_id for item in progress if item.active}
        unknown_ids = active_ids - {item.technology_id for item in self.technologies}
        if unknown_ids:
            names = ", ".join(sorted(unknown_ids))
            raise ValueError(f"active technologies are outside this graph: {names}")
        return prod(
            self.definition(technology_id).effect_multiplier(kind)
            for technology_id in sorted(active_ids)
        )

    def maintenance_cost(
        self,
        progress: Iterable[TechnologyProgress],
    ) -> ResourceInventory:
        """Return the combined per-step cost of all active technologies."""

        active_ids = {item.technology_id for item in progress if item.active}
        unknown_ids = active_ids - {item.technology_id for item in self.technologies}
        if unknown_ids:
            names = ", ".join(sorted(unknown_ids))
            raise ValueError(f"active technologies are outside this graph: {names}")

        costs = [self.definition(technology_id).maintenance_cost for technology_id in sorted(active_ids)]
        return ResourceInventory(
            food=sum(cost.food for cost in costs),
            wood=sum(cost.wood for cost in costs),
            stone=sum(cost.stone for cost in costs),
        )


def starter_technology_graph() -> TechnologyGraph:
    """Return the intentionally small four-node graph used by Level 1."""

    return TechnologyGraph(
        technologies=(
            TechnologyDefinition(
                technology_id="fire",
                name="Fire",
                description="Basic controlled fire that improves the value of prepared food.",
                discovery_cost=ResourceInventory(wood=8.0),
                maintenance_cost=ResourceInventory(wood=0.1),
                discovery_labor=4.0,
                base_discovery_rate=0.12,
                effects=(
                    TechnologyEffect(
                        TechnologyEffectKind.FOOD_VALUE_MULTIPLIER,
                        1.10,
                    ),
                ),
            ),
            TechnologyDefinition(
                technology_id="cooking",
                name="Cooking",
                description="Prepared food provides more usable nutrition.",
                prerequisites=frozenset({"fire"}),
                discovery_cost=ResourceInventory(food=4.0, wood=5.0),
                maintenance_cost=ResourceInventory(wood=0.05),
                discovery_labor=6.0,
                base_discovery_rate=0.09,
                effects=(
                    TechnologyEffect(
                        TechnologyEffectKind.FOOD_VALUE_MULTIPLIER,
                        1.25,
                    ),
                ),
            ),
            TechnologyDefinition(
                technology_id="basic_tools",
                name="Basic tools",
                description="Simple implements increase resource-gathering yield.",
                discovery_cost=ResourceInventory(wood=5.0, stone=8.0),
                maintenance_cost=ResourceInventory(wood=0.05, stone=0.05),
                discovery_labor=5.0,
                base_discovery_rate=0.10,
                effects=(
                    TechnologyEffect(
                        TechnologyEffectKind.GATHER_YIELD_MULTIPLIER,
                        1.25,
                    ),
                ),
            ),
            TechnologyDefinition(
                technology_id="storage",
                name="Storage",
                description="Protected stores reduce passive resource loss.",
                prerequisites=frozenset({"basic_tools"}),
                discovery_cost=ResourceInventory(wood=10.0, stone=5.0),
                maintenance_cost=ResourceInventory(wood=0.1),
                discovery_labor=6.0,
                base_discovery_rate=0.08,
                effects=(
                    TechnologyEffect(
                        TechnologyEffectKind.RESOURCE_DECAY_MULTIPLIER,
                        0.50,
                    ),
                ),
            ),
        )
    )
