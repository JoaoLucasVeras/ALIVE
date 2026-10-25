"""Outcome-based reward with separately recorded components."""

from dataclasses import dataclass
from math import isfinite
from .resolver import StepOutcome
from .world import WorldState


@dataclass(frozen=True)
class RewardConfig:
    population_weight: float = 1.0
    shortage_weight: float = 0.5
    loss_weight: float = 2.0

    def __post_init__(self):
        if any(not isfinite(x) or x < 0 for x in
               (self.population_weight, self.shortage_weight, self.loss_weight)):
            raise ValueError("reward weights must be finite and non-negative")


def reward_components(before: WorldState, outcome: StepOutcome,
                      initial_population: float,
                      config: RewardConfig = RewardConfig()) -> dict[str, float]:
    if initial_population <= 0:
        raise ValueError("initial population must be positive")
    return {
        "population": config.population_weight * outcome.next_state.community.population / initial_population,
        "shortage": -config.shortage_weight * outcome.food_shortage / max(1.0, initial_population * 0.05),
        "loss": config.loss_weight * (outcome.next_state.community.population - before.community.population) / initial_population,
    }
