"""Recorded simulation facts, same-seed comparisons, and portable exports.

No graphics or policy decisions live here. Inspection reads recorded immutable
states and never rewinds or changes the running episode.
"""

from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import csv
import json
from pathlib import Path

from .baseline_agents import RandomAgent, RuleAgent
from .environment.episode import run_episode


class RunRecording:
    def __init__(self, initial_state, scenario, controller, configuration=None):
        self.states = [initial_state]
        self.turns = []
        self.scenario = scenario
        self.controller = controller
        self.configuration = configuration or {}

    def append(self, state, reward, terminated, truncated, info):
        if state.step != self.states[-1].step + 1:
            raise ValueError("recording must append consecutive simulation turns")
        self.states.append(state)
        self.turns.append(dict(info, reward=reward, terminated=terminated, truncated=truncated))

    def summary(self, turn=None):
        turn = len(self.turns) if turn is None else turn
        if not 0 <= turn <= len(self.turns):
            raise IndexError("inspection turn is outside the recorded run")
        records = self.turns[:turn]
        initial = self.states[0].community.population
        population = self.states[turn].community.population
        last = records[-1] if records else {}
        shortage_turns = [r["step"] for r in records if r["shortage"] > 0]
        return {
            "scenario": self.scenario.name,
            "controller": self.controller,
            "seed": self.states[0].episode_seed,
            "steps": turn, "horizon": self.scenario.world_config.max_steps,
            "status": "collapsed" if last.get("terminated") else "time limit reached" if last.get("truncated") else "in progress",
            "initial_population": initial, "population": population,
            "population_retained": population / initial,
            "population_lost": initial - population,
            "shortage_turns": len(shortage_turns),
            "first_shortage": shortage_turns[0] if shortage_turns else None,
            "shortage_total": sum(r["shortage"] for r in records),
            "return": sum(r["reward"] for r in records),
            "discovered": last.get("discovered", []),
            "actions": dict(Counter(r["action"].split(":")[0] for r in records)),
        }

    def baseline_comparison(self):
        """Full reference episodes use this exact scenario/seed and no live RNG."""
        return [dict(agent=name, **run_episode(agent, self.scenario, self.states[0].episode_seed))
                for name, agent in (("random", RandomAgent()), ("rules", RuleAgent()))]

    def export(self, root="results/viewer_runs", comparisons=()):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        folder = Path(root) / f"{self.scenario.name}_seed{self.states[0].episode_seed}_{stamp}"
        folder.mkdir(parents=True, exist_ok=False)
        payload = {"format_version": 1, "summary": self.summary(),
                   "engine_configuration": self.configuration,
                   "scenario_config": asdict(self.scenario),
                   "states": [asdict(s) for s in self.states], "turns": self.turns,
                   "baseline_comparisons": list(comparisons)}
        (folder / "run.json").write_text(json.dumps(payload, indent=2, default=self._json_value), encoding="utf-8")
        with (folder / "turns.csv").open("w", newline="", encoding="utf-8") as stream:
            fields = ["step", "action", "population", "food", "wood", "stone", "shortage", "food_consumed", "movement_food_spent", "gathered_resource", "gathered_amount", "reward", "technology_completed"]
            fields += [f"{key}_{name}" for key in ('resource_changes', 'research_cost', 'maintenance_paid', 'decay_losses') for name in ('food', 'wood', 'stone')]
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for record, state in zip(self.turns, self.states[1:]):
                row = dict(record, wood=state.community.resources.wood, stone=state.community.resources.stone)
                for key in ('resource_changes', 'research_cost', 'maintenance_paid', 'decay_losses'):
                    row.update({f"{key}_{name}": value for name, value in record[key].items()})
                writer.writerow(row)
        return folder

    @staticmethod
    def _json_value(value):
        if isinstance(value, (set, frozenset)):
            return sorted(value)
        raise TypeError(f"unsupported export value: {type(value).__name__}")


CONTROLLERS = {
    "rules": ("RULE-BASED", "A hand-written survival strategy. No learning occurs in this viewer."),
    "random": ("RANDOM", "Chooses uniformly among legal actions. A reference for comparison."),
    "manual": ("YOU CONTROL", "Choose each action yourself; the same costs and rules apply."),
    "rl": ("TRAINED RL", "A saved recurrent policy. Memory updates; training weights stay fixed."),
}


def turn_explanation(record):
    if record is None:
        return "Initial state: no action or resource cost has occurred yet."
    action = record["action"].split(":")
    if action[0] == "gather":
        return f"Collected {record['gathered_amount']:.1f} {action[1]}; consumption and decay then apply."
    if action[0] == "move":
        return f"Moved {action[1]}; travel used {record['movement_food_spent']:.2f} food."
    if action[0] == "experiment":
        return f"Researched {action[1].replace('_', ' ')}. Upfront cost applies only on the first attempt."
    return "Conserved: reduced food consumption this turn; no gathering or research."
