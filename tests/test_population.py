"""Version 1.3 population dynamics: births, deaths, and labour-scaled gathering."""

import unittest
from dataclasses import replace

from alive.baseline_agents import RuleAgent
from alive.environment.episode import Episode, run_episode
from alive.environment.resolver import ActionResolver, ResolverConfig
from alive.environment.scenarios import stable_scenario


def run(config, seed=42):
    return run_episode(RuleAgent(), stable_scenario(), seed, ActionResolver(config))


class PopulationDynamicsTests(unittest.TestCase):
    def test_default_config_is_unchanged_version_1(self):
        config = ResolverConfig()
        self.assertFalse(config.population_dynamics_enabled)
        result = run(config)
        self.assertTrue(all("births" not in r for r in result["trace"]))
        self.assertEqual(result["trace"], run_episode(RuleAgent(), stable_scenario(), 42)["trace"])

    def test_invalid_parameters_rejected(self):
        for bad in ({"birth_rate_per_step": 1.5}, {"max_population": 0}, {"max_labor_multiplier": 0.5}):
            with self.assertRaises(ValueError):
                ResolverConfig(**bad)

    def test_births_happen_and_respect_cap_and_ledger(self):
        config = ResolverConfig.with_population_dynamics()
        result = run(config)
        trace = result["trace"]
        self.assertGreater(sum(r["births"] for r in trace), 0)
        self.assertLessEqual(max(r["population"] for r in trace), config.max_population)
        previous = 40.0
        for r in trace:
            self.assertAlmostEqual(
                r["population"] - previous,
                r["births"] - r["starvation_deaths"] - r["natural_deaths"],
            )
            self.assertAlmostEqual(r["labor"], r["population"] * 0.6)
            previous = r["population"]

    def test_no_births_during_shortage(self):
        trace = run(ResolverConfig.with_population_dynamics(), seed=7)["trace"]
        for r in trace:
            if r["shortage"] > 0:
                self.assertEqual(r["births"], 0.0)

    def test_births_cost_food_and_ledger_reconciles(self):
        trace = run(ResolverConfig.with_population_dynamics())["trace"]
        self.assertTrue(any(r["birth_food_spent"] > 0 for r in trace))
        for r in trace:
            gain = r["gathered_amount"] if r["gathered_resource"] == "food" else 0
            costs = (r["research_cost"]["food"] + r["maintenance_paid"]["food"] + r["decay_losses"]["food"]
                     + r["food_consumed"] + r["movement_food_spent"] + r["birth_food_spent"])
            self.assertAlmostEqual(r["resource_changes"]["food"], gain - costs)

    def test_labour_scales_gathering(self):
        base = run(ResolverConfig())["trace"]
        grown = run(ResolverConfig(labor_scales_gathering=True, birth_rate_per_step=0.05))["trace"]
        self.assertTrue(any(r["labor_multiplier"] > 1.0 for r in grown))
        self.assertTrue(all(r["labor_multiplier"] <= 2.0 for r in grown))
        self.assertTrue(all("labor_multiplier" not in r for r in base))

    def test_collapse_still_possible(self):
        harsh = ResolverConfig.with_population_dynamics(natural_death_rate_per_step=1.0)
        result = run(harsh)
        self.assertTrue(result["terminated"])

    def test_deterministic(self):
        config = ResolverConfig.with_population_dynamics()
        self.assertEqual(run(config)["trace"], run(config)["trace"])

    def test_growth_aware_agent_is_default_identical_without_growth_and_evaluates(self):
        from alive.baseline_agents import GrowthAwareRuleAgent
        import tempfile, json
        from alive.evaluate import evaluate
        plain = run_episode(RuleAgent(), stable_scenario(), 42)["trace"]
        self.assertEqual(plain, run_episode(RuleAgent(), stable_scenario(), 42)["trace"])
        with tempfile.TemporaryDirectory() as out:
            summary = evaluate(episodes=2, output=out, population_dynamics=True)
            self.assertIn("rules_growth_aware", [row["agent"] for row in summary])
            config = json.load(open(out + "/configuration.json", encoding="utf-8"))
            self.assertTrue(config["population_dynamics"])
            run = json.load(open(out + "/runs/rules_seed_10000.json", encoding="utf-8"))
            self.assertIn("births", run["trace"][0])


if __name__ == "__main__":
    unittest.main()
