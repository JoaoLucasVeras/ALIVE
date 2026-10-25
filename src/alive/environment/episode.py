"""Dependency-free reset/step interface and complete episode runner."""

from dataclasses import dataclass, asdict
from typing import Protocol
from .observations import Observation, observe
from .rewards import RewardConfig, reward_components
from .resolver import ActionResolver
from .scenarios import ScenarioDefinition, scenario_by_name


class Agent(Protocol):
    def reset(self, seed: int) -> None: ...
    def act(self, observation: Observation) -> int: ...


class Episode:
    def __init__(self, scenario: ScenarioDefinition | None = None,
                 resolver: ActionResolver | None = None,
                 reward_config: RewardConfig = RewardConfig()):
        self.scenario = scenario or scenario_by_name("stable")
        self.resolver = resolver or ActionResolver()
        self.reward_config = reward_config
        self.instance = None

    def reset(self, seed: int = 0) -> Observation:
        self.instance = self.scenario.generate(seed)
        self.state = self.instance.initial_state
        return observe(self.instance.world, self.state)

    def step(self, index: int):
        if self.instance is None:
            raise RuntimeError("call reset before step")
        world = self.instance.world
        if world.is_terminal(self.state):
            raise RuntimeError("episode is complete; call reset")
        observation = observe(world, self.state)
        action = world.action_catalog.require_legal(index, world.legal_action_mask(self.state))
        outcome = self.resolver.resolve(world, self.state, action)
        before = self.state
        research_cost = {"food": 0.0, "wood": 0.0, "stone": 0.0}
        if outcome.experiment_technology_id and before.community.technology(outcome.experiment_technology_id) is None:
            research_cost = asdict(world.technology_graph.definition(outcome.experiment_technology_id).discovery_cost)
        components = reward_components(self.state, outcome,
                                       world.config.starting_population, self.reward_config)
        self.state = outcome.next_state
        terminated = not self.state.community.active
        truncated = self.state.step >= world.config.max_steps and not terminated
        info = {
            "action": action.label, "step": self.state.step,
            "population": self.state.community.population,
            "food": self.state.community.resources.food,
            "position": asdict(self.state.community.position),
            "reward_components": components,
            "shortage": outcome.food_shortage,
            "technology_completed": outcome.technology_completed,
            "discovered": [p.technology_id for p in self.state.community.technologies if p.discovery_progress == 1],
            "population_change": outcome.population_change,
            "food_consumed": outcome.food_consumed,
            "movement_food_spent": outcome.movement_food_spent,
            "maintenance_paid": asdict(outcome.maintenance_paid),
            "research_cost": research_cost,
            "gathered_resource": outcome.gathered_resource.value if outcome.gathered_resource else None,
            "gathered_amount": outcome.gathered_amount,
            "resource_changes": {name: getattr(self.state.community.resources, name) - getattr(before.community.resources, name)
                                 for name in ("food", "wood", "stone")},
        }
        info["decay_losses"] = {
            name: max(0.0, getattr(before.community.resources, name)
                      + (outcome.gathered_amount if info["gathered_resource"] == name else 0)
                      - research_cost[name] - info["maintenance_paid"][name]
                      - (outcome.food_consumed + outcome.movement_food_spent if name == "food" else 0)
                      - getattr(self.state.community.resources, name))
            for name in ("food", "wood", "stone")
        }
        return observe(world, self.state), sum(components.values()), terminated, truncated, info


def run_episode(agent: Agent, scenario: ScenarioDefinition, seed: int,
                resolver: ActionResolver | None = None) -> dict:
    episode = Episode(scenario, resolver)
    observation = episode.reset(seed)
    agent.reset(seed)
    records = []
    total = 0.0
    while True:
        observation, reward, terminated, truncated, info = episode.step(agent.act(observation))
        records.append(info)
        total += reward
        if terminated or truncated:
            break
    return {
        "scenario": scenario.name, "seed": seed, "return": total,
        "steps": episode.state.step,
        "population_retained": episode.state.community.population / scenario.world_config.starting_population,
        "shortage_total": sum(r["shortage"] for r in records),
        "discovered": records[-1]["discovered"],
        "terminated": terminated, "truncated": truncated, "trace": records,
    }
