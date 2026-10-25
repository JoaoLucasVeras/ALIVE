"""Behavior and integration tests; run with unittest discovery."""

import json
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from dataclasses import replace
from alive.environment.models import Position, Resource, ResourceInventory, TechnologyProgress
from alive.environment.actions import Action
from alive.environment.scenarios import stable_scenario, scarcity_scenario
from alive.environment.observations import observe
from alive.environment.episode import Episode, run_episode
from alive.environment.resolver import ActionResolver
from alive.environment.world import ResourceDeposit
from alive.evaluate import evaluate
from alive.baseline_agents import RandomAgent, RuleAgent


class SimulationTests(unittest.TestCase):
    def test_seed_reproducibility(self):
        scenario = stable_scenario()
        self.assertEqual(scenario.generate(42).initial_state, scenario.generate(42).initial_state)
        self.assertNotEqual(scenario.generate(42).initial_state, scenario.generate(43).initial_state)

    def test_hidden_information_does_not_change_observation(self):
        i = stable_scenario().generate(42)
        distant = ResourceDeposit(Position(0, 0), Resource.FOOD, 1, 100)
        deposits = tuple(d for d in i.initial_state.deposits if d.key != distant.key)
        a = replace(i.initial_state, deposits=deposits + (distant,))
        b = replace(a, deposits=deposits + (replace(distant, amount=99),))
        self.assertEqual(observe(i.world, a), observe(i.world, b))

    def test_observation_shape_and_bounds(self):
        a = Episode(stable_scenario()).reset(1)
        b = Episode(scarcity_scenario()).reset(2)
        self.assertEqual(a.names, b.names)
        self.assertEqual(len(a.values), 128)
        self.assertTrue(all(0 <= v <= 1 for v in a.values))

    def test_resource_accounting_and_immutability(self):
        i = stable_scenario().generate(0)
        before = i.initial_state
        deposit = before.deposit_at(before.community.position, Resource.FOOD)
        out = ActionResolver().resolve(i.world, before, Action.gather(Resource.FOOD))
        after = out.next_state.deposit_at(before.community.position, Resource.FOOD)
        self.assertAlmostEqual(after.amount, min(deposit.capacity, deposit.amount - out.gathered_amount + deposit.regeneration_per_step))
        self.assertEqual(before.step, 0)
        self.assertEqual(out.next_state.step, 1)

    def test_upfront_research_paid_once(self):
        i = stable_scenario().generate(0)
        state = i.initial_state
        a = ActionResolver().resolve(i.world, state, Action.experiment("fire"))
        b = ActionResolver().resolve(i.world, a.next_state, Action.experiment("fire"))
        self.assertAlmostEqual(b.next_state.community.resources.wood, a.next_state.community.resources.wood * 0.99)
        self.assertAlmostEqual(b.next_state.community.technology("fire").discovery_progress, 0.24)

    def test_illegal_action_and_finished_episode(self):
        e = Episode()
        e.reset(0)
        with self.assertRaises(ValueError):
            e.step(e.instance.world.action_catalog.encode(Action.experiment("cooking")))
        e.state = replace(e.state, step=256)
        with self.assertRaises(RuntimeError):
            e.step(11)

    def test_baselines_complete_and_replay(self):
        for cls in (RandomAgent, RuleAgent):
            for scenario in (stable_scenario(), scarcity_scenario()):
                result = run_episode(cls(), scenario, 10)
                self.assertEqual(result, run_episode(cls(), scenario, 10))
                self.assertLessEqual(result["steps"], 256)
                self.assertTrue(result["terminated"] or result["truncated"])
                if result["terminated"]:
                    self.assertEqual(result["population_retained"], 0)
                self.assertGreaterEqual(result["population_retained"], 0)

    def test_rule_baseline_escapes_depleted_food_and_advances_technology(self):
        result = run_episode(RuleAgent(), stable_scenario(), 42)
        self.assertTrue(
            {"fire", "cooking", "basic_tools"} <= set(result["discovered"])
        )
        self.assertGreater(result["population_retained"], 0.5)

        longest_stagnant_gather = current_streak = 0
        previous_position = None
        for record in result["trace"]:
            position = tuple(record["position"].values())
            if record["action"] == "gather:food" and position == previous_position:
                current_streak += 1
            elif record["action"] == "gather:food":
                current_streak = 1
            else:
                current_streak = 0
            longest_stagnant_gather = max(longest_stagnant_gather, current_streak)
            previous_position = position

        self.assertLessEqual(longest_stagnant_gather, 8)
        self.assertFalse(
            any(
                record["action"] == "gather:food"
                and record["gathered_amount"] < 1.0
                for record in result["trace"]
            )
        )

    def test_technology_ablation_preserves_paired_runs_and_full_traces(self):
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(io.StringIO()):
                summaries = evaluate(
                    scenario="stable",
                    episodes=2,
                    seed_start=42,
                    output=directory,
                    technology_ablation=True,
                )
            self.assertEqual(
                {summary["agent"] for summary in summaries},
                {"random", "rules", "rules_no_research"},
            )
            comparison = json.loads(
                (Path(directory) / "technology_comparison.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual([pair["seed"] for pair in comparison["pairs"]], [42, 43])
            restricted = json.loads(
                (Path(directory) / "runs" / "rules_no_research_seed_42.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(restricted["discovered"], [])
            self.assertEqual(len(restricted["trace"]), restricted["steps"])
            self.assertFalse(
                any(
                    record["action"].startswith("experiment:")
                    for record in restricted["trace"]
                )
            )


class OptionalRLTests(unittest.TestCase):
    def test_gym_contract(self):
        try:
            from gymnasium.utils.env_checker import check_env
            from alive.environment.rl_environment import AliveEnv
        except ImportError:
            self.skipTest("optional RL packages unavailable")
        # Checker samples unmasked actions, which this environment rejects.
        env = AliveEnv()
        obs, info = env.reset(seed=42)
        self.assertTrue(env.observation_space.contains(obs))
        obs, reward, terminated, truncated, info = env.step(11)
        self.assertTrue(env.observation_space.contains(obs))
        self.assertTrue(info["action_mask"][11])

    def test_masked_recurrence_and_gradients(self):
        try:
            import torch
            from alive.rl_policy import RecurrentPolicy
        except ImportError:
            self.skipTest("optional PyTorch unavailable")
        policy = RecurrentPolicy(3, 2, 8)
        x = torch.randn(1, 4, 3)
        mask = torch.tensor([[[True, False]] * 4])
        dist, value, hidden = policy(x, mask)
        self.assertTrue(torch.all(dist.sample() == 0))
        (value.square().mean() - dist.entropy().mean()).backward()
        self.assertTrue(torch.isfinite(policy.memory.weight_ih_l0.grad).all())
        _, first, h = policy(x[:, :2], mask[:, :2])
        _, second, _ = policy(x[:, 2:], mask[:, 2:], h)
        self.assertTrue(torch.allclose(value, torch.cat((first, second), dim=1), atol=1e-6))


if __name__ == "__main__":
    unittest.main()
