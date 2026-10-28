"""Reference policies using exactly the observation supplied to RL.

The rule baseline is deliberately transparent rather than optimal.  It keeps a
small memory of places it has actually observed, budgets resources before
starting research, and leaves deposits whose immediate yield is too small to
support the current population.  It never reads the hidden ``WorldState``.
"""

from random import Random
from .environment.observations import Observation


RESEARCH_STRATEGIES = {
    "none": (),
    "fire": ("fire",),
    "cooking": ("fire", "cooking"),
    "all": ("fire", "cooking", "basic_tools", "storage"),
}


class RandomAgent:
    def reset(self, seed: int):
        self.random = Random(seed + 1_000_000)

    def act(self, observation: Observation) -> int:
        return self.random.choice([i for i, legal in enumerate(observation.action_mask) if legal])


class RuleAgent(RandomAgent):
    """A yield-aware survival and research reference policy.

    The baseline has memory for visited cells and previously visible deposits,
    matching the kind of temporal information available to a recurrent RL
    policy.  Coordinates are relative to the reset position, so the policy does
    not infer the map dimensions or inspect cells outside its observation.
    """

    _RESOURCE_TARGETS = {"food": 30.0, "wood": 14.0, "stone": 12.0}
    _NEW_RESEARCH_FOOD_FLOOR = 8.0
    _RESEARCH_RESUME_FOOD_FLOOR = 6.0
    _FOOD_TARGET_BASE = 20.0
    _FOOD_TARGET_SLOPE = 10.0
    _USEFUL_YIELD_SCALE = 1.5

    def __init__(self, *, research_enabled: bool = True, research_strategy: str = "all"):
        if not isinstance(research_enabled, bool):
            raise TypeError("research_enabled must be a boolean")
        if research_strategy not in RESEARCH_STRATEGIES:
            raise ValueError(f"unknown research strategy: {research_strategy!r}")
        if not research_enabled and research_strategy not in ("all", "none"):
            raise ValueError("research_enabled=False conflicts with a restricted research strategy")
        self.research_strategy = research_strategy if research_enabled else "none"
        self.research_enabled = self.research_strategy != "none"
        self._research_order = RESEARCH_STRATEGIES[self.research_strategy]

    def reset(self, seed: int):
        super().reset(seed)
        self.position = (0, 0)
        self.visit_counts: dict[tuple[int, int], int] = {}
        self.known_deposits: dict[tuple[str, int, int], float] = {}

    @staticmethod
    def _raw(normalized: float) -> float:
        """Invert the fixed ``amount / (amount + 30)`` observation scale."""

        return 30.0 * normalized / max(1e-9, 1.0 - normalized)

    def _remember_visible_deposits(self, features: dict[str, float]) -> None:
        radius = max(
            abs(int(name.split(":")[1]))
            for name in features
            if name.startswith("cell:") and name.endswith(":visible")
        )
        px, py = self.position
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if not features.get(f"cell:{dx}:{dy}:visible", 0.0):
                    continue
                for resource in self._RESOURCE_TARGETS:
                    key = (resource, px + dx, py + dy)
                    amount = self._raw(features[f"cell:{dx}:{dy}:{resource}"])
                    if amount > 1e-6:
                        self.known_deposits[key] = amount
                    else:
                        self.known_deposits.pop(key, None)

    def _move_index(
        self,
        direction: str,
        legal: dict[str, int],
    ) -> int | None:
        label = f"move:{direction}"
        if label not in legal:
            return None
        dx, dy = {
            "north": (0, -1), "south": (0, 1),
            "east": (1, 0), "west": (-1, 0),
        }[direction]
        self.position = (self.position[0] + dx, self.position[1] + dy)
        return legal[label]

    def _move_toward(
        self,
        target: tuple[int, int],
        legal: dict[str, int],
    ) -> int | None:
        px, py = self.position
        dx, dy = target[0] - px, target[1] - py
        directions = []
        if dx:
            directions.append("east" if dx > 0 else "west")
        if dy:
            directions.append("south" if dy > 0 else "north")
        directions.sort(
            key=lambda direction: self.visit_counts.get(
                {
                    "north": (px, py - 1), "south": (px, py + 1),
                    "east": (px + 1, py), "west": (px - 1, py),
                }[direction],
                0,
            )
        )
        for direction in directions:
            index = self._move_index(direction, legal)
            if index is not None:
                return index
        return None

    def _explore(self, features: dict[str, float], legal: dict[str, int]) -> int:
        opposite = {"north": "south", "south": "north", "east": "west", "west": "east"}
        px, py = self.position
        candidates = []
        for direction, (dx, dy) in {
            "north": (0, -1), "south": (0, 1),
            "east": (1, 0), "west": (-1, 0),
        }.items():
            label = f"move:{direction}"
            if label not in legal:
                continue
            reversed_last_move = features.get(
                f"previous:move:{opposite[direction]}", 0.0
            )
            candidates.append(
                (
                    self.visit_counts.get((px + dx, py + dy), 0),
                    int(bool(reversed_last_move)),
                    self.random.random(),
                    direction,
                )
            )
        if not candidates:
            return legal["conserve"]
        return self._move_index(min(candidates)[-1], legal)  # type: ignore[return-value]

    def act(self, observation: Observation) -> int:
        f = observation.as_dict()
        labels = [n.removeprefix("previous:") for n in observation.names if n.startswith("previous:")]
        legal = {labels[i]: i for i, value in enumerate(observation.action_mask) if value}
        self.visit_counts[self.position] = self.visit_counts.get(self.position, 0) + 1
        self._remember_visible_deposits(f)

        resources = {
            resource: self._raw(f[resource]) for resource in self._RESOURCE_TARGETS
        }

        # Once research has started, finish it while food remains above the
        # emergency floor.  If the floor is crossed, replenish and resume later.
        if self.research_enabled:
            for technology_id in self._research_order:
                progress = f[f"tech:{technology_id}:progress"]
                label = f"experiment:{technology_id}"
                if (
                    0.0 < progress < 1.0
                    and resources["food"] >= self._RESEARCH_RESUME_FOOD_FLOOR
                    and label in legal
                ):
                    return legal[label]

        # Start a new node only after building a survival/resource budget.  This
        # starts a resumable work session rather than requiring enough food for
        # the entire discovery in one uninterrupted block.
        legal_research = (
            [
                technology_id
                for technology_id in self._research_order
                if f"experiment:{technology_id}" in legal
            ]
            if self.research_enabled
            else []
        )
        if legal_research and resources["food"] >= self._NEW_RESEARCH_FOOD_FLOOR:
            return legal[f"experiment:{legal_research[0]}"]

        population_ratio = f["population"]
        targets = dict(self._RESOURCE_TARGETS)
        targets["food"] = self._FOOD_TARGET_BASE + self._FOOD_TARGET_SLOPE * population_ratio
        target = (
            "food"
            if legal_research
            else max(
                targets,
                key=lambda resource: (
                    targets[resource] - resources[resource]
                ) / targets[resource],
            )
        )

        # A deposit that supplies materially less than one step of food demand
        # should not hold the policy forever simply because gathering remains legal.
        useful_yield = max(1.0, self._USEFUL_YIELD_SCALE * population_ratio)
        current_amount = self._raw(f[f"cell:0:0:{target}"])
        gather = f"gather:{target}"
        if gather in legal and current_amount >= useful_yield:
            return legal[gather]

        px, py = self.position
        destinations = [
            (amount - 0.75 * (abs(x - px) + abs(y - py)), -abs(x - px) - abs(y - py), x, y)
            for (resource, x, y), amount in self.known_deposits.items()
            if resource == target and amount >= useful_yield and (x, y) != self.position
        ]
        if destinations:
            _, _, x, y = max(destinations)
            movement = self._move_toward((x, y), legal)
            if movement is not None:
                return movement

        return self._explore(f, legal)


class GrowthAwareRuleAgent(RuleAgent):
    """Version 1.3 reference: keeps a larger food buffer for a growing community.

    The observation caps population at its starting value, so this agent cannot
    see growth directly. It instead holds a bigger food reserve and starts
    research later, so births and bigger appetites do not exhaust food.
    """

    _FOOD_TARGET_BASE = 35.0
    _FOOD_TARGET_SLOPE = 15.0
    _NEW_RESEARCH_FOOD_FLOOR = 14.0
    _RESEARCH_RESUME_FOOD_FLOOR = 10.0
