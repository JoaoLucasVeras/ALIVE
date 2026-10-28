"""Research strategy contracts, written before the implementation."""

import io
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path

from alive.baseline_agents import RuleAgent
from alive.environment.episode import Episode, run_episode
from alive.environment.models import ResourceInventory, TechnologyProgress
from alive.environment.observations import observe
from alive.environment.scenarios import stable_scenario, scarcity_scenario
from alive.evaluate import evaluate


class ResearchStrategyTests(unittest.TestCase):
    def test_invalid_strategy_and_conflicting_legacy_switch_rejected(self):
        with self.assertRaises(ValueError):
            RuleAgent(research_strategy="unknown")
        with self.assertRaises(ValueError):
            RuleAgent(research_strategy="fire", research_enabled=False)

    def test_defaults_and_legacy_switch_preserve_complete_traces(self):
        scenario = stable_scenario()
        # Captured before implementation from the original complete seed-42 traces.
        for enabled, expected in ((True, "6ad021907d891e25b9dc023bb50b75855eb73a525cd6901869ab8de1f5c4d0c2"),
                                  (False, "75a44aaa88187c0a44a256666ee74c895cd1fb79bb2f1bc0423e09d336aa0203")):
            original = run_episode(RuleAgent(research_enabled=enabled), scenario, 42)
            self.assertEqual(hashlib.sha256(json.dumps(original, sort_keys=True).encode()).hexdigest(), expected)
        self.assertEqual(run_episode(RuleAgent(), scenario, 42),
                         run_episode(RuleAgent(research_strategy="all"), scenario, 42))
        self.assertEqual(run_episode(RuleAgent(research_enabled=False), scenario, 42),
                         run_episode(RuleAgent(research_strategy="none"), scenario, 42))

    def test_each_strategy_reproducible_and_restricted_in_both_scenarios(self):
        allowed = {"none": set(), "fire": {"fire"},
                   "cooking": {"fire", "cooking"},
                   "all": {"fire", "cooking", "basic_tools", "storage"}}
        for scenario in (stable_scenario(), scarcity_scenario()):
            for strategy, technologies in allowed.items():
                with self.subTest(scenario=scenario.name, strategy=strategy):
                    run = run_episode(RuleAgent(research_strategy=strategy), scenario, 42)
                    self.assertEqual(run, run_episode(RuleAgent(research_strategy=strategy), scenario, 42))
                    experiments = {r["action"].split(":")[1] for r in run["trace"]
                                   if r["action"].startswith("experiment:")}
                    self.assertLessEqual(experiments, technologies)
                    self.assertLessEqual(set(run["discovered"]), technologies)
                    if scenario.name == "stable":
                        self.assertEqual(experiments, technologies if strategy != "all" else {"fire", "cooking", "basic_tools"})

    def test_cooking_requires_fire_and_restricted_progress_is_not_resumed(self):
        episode = Episode()
        observation = episode.reset(42)
        agent = RuleAgent(research_strategy="cooking")
        agent.reset(42)
        labels = episode.instance.world.action_catalog.labels
        self.assertEqual(labels[agent.act(observation)], "experiment:fire")
        self.assertFalse(observation.action_mask[labels.index("experiment:cooking")])
        community = replace(episode.state.community,
                            resources=ResourceInventory(food=30, wood=30, stone=30),
                            technologies=(TechnologyProgress("fire", discovery_progress=1, active=True),
                                          TechnologyProgress("basic_tools", discovery_progress=0.5)))
        observation = observe(episode.instance.world, replace(episode.state, community=community))
        self.assertEqual(labels[agent.act(observation)], "experiment:cooking")
        agent = RuleAgent(research_strategy="fire")
        agent.reset(42)
        self.assertFalse(labels[agent.act(observation)].startswith("experiment:"))


class ResearchEvaluationTests(unittest.TestCase):
    def test_comparison_exports_paired_runs_configuration_and_report(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            summaries = evaluate(episodes=2, seed_start=42, output=directory,
                                 compare_research_strategies=True)
            path = Path(directory)
            config = json.loads((path / "configuration.json").read_text())
            self.assertEqual(config["research_strategies"],
                             {"rules_none": "none", "rules_fire": "fire",
                              "rules_cooking": "cooking", "rules_all": "all"})
            self.assertEqual(config["seeds"], [42, 43])
            self.assertEqual(len(summaries), 5)  # Random plus four research strategies.
            for name, strategy in config["research_strategies"].items():
                for seed in config["seeds"]:
                    run = json.loads((path / "runs" / f"{name}_seed_{seed}.json").read_text())
                    self.assertEqual(run["research_strategy"], strategy)
                    self.assertEqual(run["seed"], seed)
                    self.assertEqual(len(run["trace"]), run["steps"])
                    self.assertEqual({k: v for k, v in run.items() if k != "research_strategy"},
                                     run_episode(RuleAgent(research_strategy=strategy), stable_scenario(), seed))
            comparison = json.loads((path / "research_comparison.json").read_text())
            self.assertEqual(comparison["reference_agent"], "rules_none")
            by_name = {row["agent"]: row for row in summaries}
            for result in comparison["comparisons"]:
                self.assertEqual([p["seed"] for p in result["pairs"]], [42, 43])
                self.assertAlmostEqual(result["mean_population_retained_delta"],
                                       by_name[result["agent"]]["mean_population_retained"] -
                                       by_name["rules_none"]["mean_population_retained"])
                self.assertEqual(result["wins"] + result["losses"] + result["ties"], 2)
            self.assertIn("research_strategy", (path / "episodes.csv").read_text())
            self.assertIn("Research strategy comparison", (path / "report.html").read_text())
            self.assertIn("Mean shortage", (path / "report.html").read_text())
            self.assertIn("Retention SD", (path / "report.html").read_text())

    def test_ambiguous_modes_rejected_before_creating_outputs(self):
        for options in ({"research_strategy": "fire", "technology_ablation": True},
                        {"research_strategy": "fire", "compare_research_strategies": True},
                        {"technology_ablation": True, "compare_research_strategies": True},
                        {"research_strategy": "invalid"}):
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "absent"
                with self.assertRaises(ValueError):
                    evaluate(output=output, **options)
                self.assertFalse(output.exists())

    def test_cli_selects_one_strategy_and_rejects_unknown_values(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, "-m", "alive.evaluate", "--episodes", "1",
                                     "--research-strategy", "fire", "--output", directory],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            config = json.loads((Path(directory) / "configuration.json").read_text())
            self.assertEqual(config["research_strategies"], {"rules": "fire"})
            result = subprocess.run([sys.executable, "-m", "alive.evaluate", "--research-strategy", "bad"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
