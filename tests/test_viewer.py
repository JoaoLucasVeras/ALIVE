"""Optional viewer tests use SDL's off-screen driver, not a visible window."""

import os
import unittest
import json
import tempfile
from alive.environment.episode import run_episode
from alive.environment.scenarios import stable_scenario
from alive.baseline_agents import RuleAgent


class ViewerTests(unittest.TestCase):
    def setUp(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        try:
            import pygame
            from alive.viewer import Viewer
        except ImportError:
            self.skipTest("install .[viewer] to run viewer tests")
        self.pygame = pygame
        self.viewer = Viewer(seed=42)

    def tearDown(self):
        if hasattr(self, "pygame"):
            self.pygame.quit()

    def test_viewer_matches_simulation_and_stops(self):
        expected = run_episode(RuleAgent(), stable_scenario(), 42)
        while self.viewer.step():
            self.viewer.update(0.1)
        self.assertEqual(self.viewer.episode.state.step, expected["steps"])
        self.assertAlmostEqual(self.viewer.episode.state.community.population / 40,
                               expected["population_retained"])
        self.assertFalse(self.viewer.playing)
        self.viewer.draw()

    def test_pause_restart_and_manual_controls(self):
        viewer = self.viewer
        viewer.update(2)
        self.assertEqual(viewer.episode.state.step, 0)
        viewer.toggle_play()
        viewer.update(1)
        self.assertEqual(viewer.episode.state.step, 1)
        viewer.reset()
        self.assertEqual(viewer.episode.state.step, 0)
        viewer.controller = "manual"
        viewer.reset()
        viewer.handle(self.pygame.event.Event(self.pygame.KEYDOWN, key=self.pygame.K_1))
        self.assertEqual(viewer.episode.state.step, 1)
        self.assertEqual(viewer.episode.state.community.previous_action, "gather:food")
        viewer.handle(self.pygame.event.Event(self.pygame.KEYDOWN, key=self.pygame.K_5))
        self.assertEqual(viewer.episode.state.step, 1)  # Cooking remains illegal.
        viewer.fog = True
        viewer.draw()

    def test_inspection_never_rewinds_or_advances_live_episode(self):
        viewer = self.viewer
        for _ in range(20):
            viewer.step()
        live = viewer.episode.state
        viewer.inspect(3)
        self.assertEqual(viewer.displayed_state.step, 3)
        self.assertFalse(viewer.playing)
        viewer.update(2)
        self.assertEqual(viewer.episode.state, live)
        for tab in ("Watch", "Results", "Guide"):
            viewer.select_tab(tab)
            viewer.draw()
        viewer.select_tab("Watch")
        viewer.single_step()
        self.assertIsNone(viewer.inspection)
        self.assertEqual(viewer.episode.state.step, 21)

    def test_comparison_and_export_preserve_live_run(self):
        viewer = self.viewer
        for _ in range(8):
            viewer.step()
        live = viewer.episode.state
        viewer.compare()
        self.assertEqual(viewer.episode.state, live)
        expected = run_episode(RuleAgent(), stable_scenario(), 42)
        self.assertEqual(viewer.comparisons[1]['trace'], expected['trace'])
        viewer.select_tab("Results")
        viewer.draw()
        with tempfile.TemporaryDirectory() as root:
            folder = viewer.recording.export(root, viewer.comparisons)
            data = json.loads((folder / 'run.json').read_text(encoding='utf-8'))
            self.assertEqual(data['summary']['steps'], 8)
            self.assertEqual(len(data['states']), 9)
            self.assertEqual(len(data['turns']), 8)
            self.assertIn('technologies', data['engine_configuration'])
            self.assertTrue((folder / 'turns.csv').exists())
        viewer.reset()
        self.assertEqual(len(viewer.recording.turns), 0)
        self.assertEqual(viewer.comparisons, [])

    def test_ledger_reconciles_every_resource_and_summary(self):
        viewer = self.viewer
        while viewer.step():
            record = viewer.recording.turns[-1]
            for name in ('food', 'wood', 'stone'):
                gain = record['gathered_amount'] if record['gathered_resource'] == name else 0
                costs = record['research_cost'][name] + record['maintenance_paid'][name] + record['decay_losses'][name]
                if name == 'food':
                    costs += record['food_consumed'] + record['movement_food_spent']
                self.assertAlmostEqual(record['resource_changes'][name], gain - costs)
        summary = viewer.recording.summary()
        self.assertEqual(summary['status'], 'time limit reached')
        self.assertEqual(summary['shortage_turns'], sum(r['shortage'] > 0 for r in viewer.recording.turns))
        self.assertEqual(viewer.recording.summary(0)['population_retained'], 1)
        viewer.select_tab('Results')
        viewer.draw()

    def test_timeline_click_and_non_watch_keys(self):
        viewer = self.viewer
        for _ in range(10):
            viewer.step()
        viewer.select_tab('Results')
        viewer.draw()
        point = (round((36 + 410) * viewer.scale + viewer.offset[0]), round(610 * viewer.scale + viewer.offset[1]))
        viewer.handle(self.pygame.event.Event(self.pygame.MOUSEBUTTONDOWN, button=1, pos=point))
        self.assertEqual(viewer.inspection, 5)
        viewer.handle(self.pygame.event.Event(self.pygame.KEYDOWN, key=self.pygame.K_n))
        self.assertEqual(viewer.episode.state.step, 10)


if __name__ == "__main__":
    unittest.main()
