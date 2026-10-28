"""Native game-style observer for the real ALIVE simulation.

Run python -m alive.viewer after installing .[viewer]. Artwork and animation
are presentation only; every decision is executed by the existing Episode.
"""

import argparse
from dataclasses import asdict
from collections import deque
from math import sin
from pathlib import Path
import random
import pygame

from .baseline_agents import RandomAgent, RuleAgent
from .environment.actions import Action
from .environment.episode import Episode
from .environment.models import Direction, Position, Resource
from .environment.resolver import ActionResolver, ResolverConfig
from .environment.scenarios import scenario_by_name
from .viewer_results import RunRecording, CONTROLLERS, turn_explanation

WIDTH, HEIGHT = 1280, 800
BG = (12, 21, 31)
PANEL = (22, 35, 48)
TEXT = (224, 236, 234)
MUTED = (146, 170, 179)
GOLD = (247, 202, 104)
GREEN = (95, 214, 154)
RED = (248, 121, 117)
RESOURCE_COLORS = {Resource.FOOD: (237, 163, 93), Resource.WOOD: (85, 183, 124), Resource.STONE: (173, 190, 207)}


class Viewer:
    """Presentation clock interpolates positions between actual simulation steps."""

    def __init__(self, scenario="stable", seed=42, controller="rules", checkpoint=None, population_dynamics=False):
        pygame.init()
        self.window = pygame.display.set_mode((1152, 720), pygame.RESIZABLE)
        pygame.display.set_caption("ALIVE | Living Worlds — Version 1.3")
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.fonts = {size: pygame.font.SysFont("Segoe UI", size) for size in (14, 16, 18, 22, 28, 38)}
        self.scenario, self.seed = scenario, seed
        self.controller, self.checkpoint = controller, checkpoint
        self.population_dynamics = population_dynamics
        self.playing = False
        self.speed = 1.0
        self.elapsed = 0.0
        self.time = 0.0
        self.fog = False
        self.buttons = []
        self.events = deque(maxlen=5)
        self.particles = []
        self.tab = "Watch"
        self.reset()

    def reset(self):
        self.playing = False
        self.episode = Episode(scenario_by_name(self.scenario), self.resolver())
        self.observation = self.episode.reset(self.seed)
        if self.controller == "rl":
            if self.population_dynamics:
                raise ValueError("RL checkpoints were trained on fixed-population rules; use rules/random/manual with growth")
            if not self.checkpoint:
                raise ValueError("RL controller requires --checkpoint")
            import torch
            from .rl_policy import PolicyAgent
            torch.set_num_threads(1)
            self.agent = PolicyAgent(self.checkpoint, self.episode)
        else:
            self.agent = RuleAgent() if self.controller == "rules" else RandomAgent()
        self.agent.reset(self.seed)
        self.previous_position = self.episode.state.community.position
        self.elapsed = 0
        self.action = "Ready to explore"
        self.events.clear()
        self.events.append("A community arrives in a new world.")
        self.particles.clear()
        self.finished = False
        self.population_history = [self.episode.state.community.population]
        self.recording = RunRecording(self.episode.state, self.episode.scenario, self.controller, {
            "resolver": asdict(self.episode.resolver.config),
            "population_dynamics": self.population_dynamics,
            "version": "1.3",
            "reward": asdict(self.episode.reward_config),
            "technologies": asdict(self.episode.instance.world.technology_graph),
            "checkpoint_path": str(self.checkpoint) if self.controller == "rl" else None,
        })
        self.inspection = None
        self.comparisons = []
        self.notice = ""

    def resolver(self):
        """Version 1.3: viewer and reference runs share one resolver configuration."""
        config = ResolverConfig.with_population_dynamics() if self.population_dynamics else ResolverConfig()
        return ActionResolver(config)

    def toggle_population_dynamics(self):
        self.population_dynamics = not self.population_dynamics
        self.playing = False
        self.reset()
        self.events.append("Population growth ON: births, deaths, labour." if self.population_dynamics else "Population growth OFF: fixed Version 1 rules.")

    @property
    def displayed_state(self):
        return self.episode.state if self.inspection is None else self.recording.states[self.inspection]

    @property
    def displayed_record(self):
        turn = self.displayed_state.step
        return self.recording.turns[turn - 1] if turn else None

    def inspect(self, turn):
        self.playing = False
        self.inspection = max(0, min(len(self.recording.turns), turn))

    def return_live(self):
        self.inspection = None

    def select_tab(self, tab):
        self.tab = tab
        self.playing = False

    def compare(self):
        self.playing = False
        self.comparisons = self.recording.baseline_comparison(self.resolver())
        self.notice = "Reference runs finished. Live episode unchanged."

    def export_run(self):
        self.playing = False
        try:
            folder = self.recording.export(comparisons=self.comparisons)
            self.notice = f"Saved JSON + CSV: {folder.name}"
        except OSError as error:
            self.notice = f"Export failed: {error}"

    @property
    def duration(self):
        return 0.8 / self.speed

    def step(self, index=None):
        if self.finished:
            return False
        if index is None:
            if self.controller == "manual":
                return False
            index = self.agent.act(self.observation)
        if not self.observation.action_mask[index]:
            self.events.append("Action unavailable here; check legal choices.")
            return False
        before = self.episode.state
        self.return_live()
        self.previous_position = before.community.position
        self.observation, reward, terminated, truncated, info = self.episode.step(index)
        self.recording.append(self.episode.state, reward, terminated, truncated, info)
        self.elapsed = 0.0
        self.action = info["action"].replace(":", " · ").replace("_", " ")
        self.finished = terminated or truncated
        self.population_history.append(info["population"])
        if info.get("births", 0) > 0 and info["step"] % 10 == 0:
            self.events.append(f"Births: +{info['births']:.2f} this turn; population {info['population']:.1f}.")
        action = info["action"]
        if action.startswith("gather:"):
            resource = Resource(action.split(":")[1])
            px, py = self.project(self.episode.state.community.position)
            rng = random.Random(self.seed * 1000 + info["step"])
            for _ in range(12):
                self.particles.append([px, py - 14, rng.uniform(-45, 45), rng.uniform(-80, -30), 0.9, RESOURCE_COLORS[resource]])
            delta = self.episode.state.community.resources.amount(resource) - before.community.resources.amount(resource)
            self.events.append(f"Gathered {resource.value}; inventory change {delta:+.1f}.")
        elif action.startswith("experiment:"):
            tid = action.split(":")[1]
            progress = self.episode.state.community.technology(tid).discovery_progress
            self.events.append(f"Experimenting with {tid.replace('_', ' ')}: {progress:.0%}.")
        if info["technology_completed"]:
            self.events.append(f"Discovered {info['technology_completed'].replace('_', ' ')}!")
        if info["shortage"] > 0:
            self.events.append(f"Food shortage: population now {info['population']:.1f}.")
        if self.finished:
            self.playing = False
            self.events.append("Community collapsed." if terminated else f"Episode complete: {info['step']} turns observed.")
        return True

    def update(self, dt):
        self.time += dt
        self.elapsed += dt
        for p in self.particles:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[4] -= dt
        self.particles = [p for p in self.particles if p[4] > 0]
        if self.playing and self.tab == "Watch" and self.inspection is None and self.controller != "manual" and self.elapsed >= self.duration:
            self.step()

    @staticmethod
    def project(pos):
        return 420 + (pos.x - pos.y) * 23, 190 + (pos.x + pos.y) * 12

    def text(self, text, x, y, size=16, color=TEXT):
        self.canvas.blit(self.fonts[size].render(str(text), True, color), (x, y))

    def button(self, label, rect, callback, active=False, enabled=True):
        box = pygame.Rect(rect)
        pygame.draw.rect(self.canvas, (48, 81, 88) if active else (32, 49, 64), box, border_radius=8)
        if not enabled:
            color = (91, 111, 120)
        else:
            color = GOLD if active else TEXT
            self.buttons.append((box, callback))
        surface = self.fonts[16].render(label, True, color)
        self.canvas.blit(surface, surface.get_rect(center=box.center))

    def toggle_play(self):
        if self.tab == "Watch" and not self.finished and self.controller != "manual":
            self.return_live()
            self.playing = not self.playing

    def single_step(self):
        self.playing = False
        self.step()

    def change_controller(self):
        modes = ["rules", "random", "manual"] + (["rl"] if self.checkpoint else [])
        self.controller = modes[(modes.index(self.controller) + 1) % len(modes)]
        self.playing = False
        self.reset()

    def change_scenario(self):
        if self.controller == "rl":
            self.events.append("Select rules/random before changing checkpoint scenario.")
            return
        self.scenario = "scarcity" if self.scenario == "stable" else "stable"
        self.playing = False
        self.reset()

    def next_seed(self):
        self.seed += 1
        self.reset()

    def change_speed(self):
        choices = [0.5, 1.0, 2.0, 4.0]
        self.speed = choices[(choices.index(self.speed) + 1) % len(choices)]

    def toggle_fog(self):
        self.fog = not self.fog

    def draw_deposit(self, deposit, x, y):
        fill = deposit.amount / deposit.capacity
        color = RESOURCE_COLORS[deposit.resource]
        if deposit.resource is Resource.WOOD:
            pygame.draw.line(self.canvas, (124, 93, 67), (x, y), (x, y - 19), 4)
            for oy, w in ((-13, 10), (-21, 8), (-28, 6)):
                pygame.draw.polygon(self.canvas, color, [(x, y + oy - 9), (x - w, y + oy + 5), (x + w, y + oy + 5)])
        elif deposit.resource is Resource.STONE:
            pygame.draw.polygon(self.canvas, color, [(x - 10, y - 2), (x - 8, y - 14), (x + 3, y - 20), (x + 11, y - 9), (x + 8, y)])
            pygame.draw.line(self.canvas, (216, 223, 225), (x - 6, y - 13), (x + 2, y - 17), 2)
        else:
            for ox in (-6, 0, 6):
                pygame.draw.line(self.canvas, (213, 180, 93), (x + ox, y), (x + ox + 2, y - 15), 2)
                pygame.draw.circle(self.canvas, color, (x + ox + 2, y - 15), 3)
        pygame.draw.rect(self.canvas, (26, 43, 47), (x - 10, y + 4, 20, 3))
        pygame.draw.rect(self.canvas, color, (x - 10, y + 4, round(20 * fill), 3))

    def draw(self):
        self.canvas.fill(BG)
        self.buttons.clear()
        self.text("ALIVE", 36, 20, 38, GOLD)
        self.text(f"VERSION 1.3  /  {self.scenario.upper()}  /  SEED {self.seed}", 165, 34, 16, MUTED)
        for i, tab in enumerate(("Watch", "Results", "Guide")):
            self.button(tab, (900 + i * 116, 26, 108, 36), lambda t=tab: self.select_tab(t), self.tab == tab)
        pygame.draw.rect(self.canvas, PANEL, (36, 80, 1208, 64), border_radius=12)
        initial = self.recording.states[0].community.population
        horizon = self.episode.scenario.world_config.max_steps
        self.text(f"GOAL: Preserve the starting {initial:g} people through {horizon} turns. Research is an optional investment.", 52, 88, 18, GOLD)
        self.text(f"{CONTROLLERS[self.controller][0]}  ·  {CONTROLLERS[self.controller][1]}", 52, 116, 14, MUTED)
        if self.tab == "Watch":
            self.draw_watch()
        elif self.tab == "Results":
            self.draw_results()
        else:
            self.draw_guide()
        self.present()

    def draw_watch(self):
        state = self.displayed_state
        cfg = self.episode.scenario.world_config
        visible = {d.key for d in self.episode.instance.world.visible_deposits(state)}
        deposits = {}
        for d in state.deposits:
            deposits.setdefault(d.position, []).append(d)
        # Isometric terrain is decorative and uses no simulation RNG.
        for diagonal in range(cfg.width + cfg.height - 1):
            for x in range(cfg.width):
                y = diagonal - x
                if not 0 <= y < cfg.height:
                    continue
                pos = Position(x, y)
                px, py = self.project(pos)
                seen = pos.manhattan_distance(state.community.position) <= cfg.observation_radius
                shade = ((x * 17 + y * 23 + self.seed) % 5) * 3
                color = (44 + shade, 79 + shade, 69 + shade)
                if self.scenario == "scarcity":
                    color = (83 + shade, 76 + shade, 54 + shade)
                if self.fog and not seen:
                    color = (24 + shade, 37 + shade, 43 + shade)
                points = [(px, py - 12), (px + 23, py), (px, py + 12), (px - 23, py)]
                pygame.draw.polygon(self.canvas, color, points)
                pygame.draw.lines(self.canvas, (35, 60, 59), True, points, 1)
                if pos == state.community.position:
                    pygame.draw.lines(self.canvas, GOLD, True, points, 2)
                items = deposits.get(pos, ())
                for index, deposit in enumerate(items):
                    if not self.fog or deposit.key in visible:
                        self.draw_deposit(deposit, px + (index - (len(items) - 1) / 2) * 11, py - index * 2)
        progress = min(1.0, self.elapsed / self.duration) if self.inspection is None else 1.0
        smooth = progress * progress * (3 - 2 * progress)
        sx, sy = self.project(self.previous_position if self.inspection is None else state.community.position)
        tx, ty = self.project(state.community.position)
        cx, cy = sx + (tx - sx) * smooth, sy + (ty - sy) * smooth
        moving = self.previous_position != state.community.position and progress < 1
        pygame.draw.ellipse(self.canvas, (17, 30, 33), (cx - 20, cy - 3, 40, 11))
        count = max(0, min(5, round(state.community.population / 8)))
        for i in range(count):
            ox, oy = ((-12, 0), (1, -9), (12, 1), (-7, 8), (8, 9))[i]
            bob = sin(self.time * (15 if moving else 3) + i) * (2 if moving else 0.6)
            px, py = cx + ox, cy + oy + bob
            coat = ((99, 190, 200), (238, 176, 105), (165, 150, 209))[i % 3]
            pygame.draw.line(self.canvas, coat, (px, py - 8), (px, py - 18), 5)
            pygame.draw.circle(self.canvas, (237, 204, 165), (round(px), round(py - 22)), 3)
            swing = sin(self.time * 15 + i) * 3 if moving else 0
            pygame.draw.line(self.canvas, TEXT, (px, py - 8), (px - 3 + swing, py), 2)
            pygame.draw.line(self.canvas, TEXT, (px, py - 8), (px + 3 - swing, py), 2)
        if self.inspection is None and self.action.startswith("experiment") and progress < 1:
            radius = 18 + int(progress * 25)
            pygame.draw.circle(self.canvas, GOLD, (round(cx), round(cy - 12)), radius, 1)
            self.text("RESEARCH", cx - 40, cy - 65, 14, GOLD)
        for p in self.particles if self.inspection is None else ():
            pygame.draw.circle(self.canvas, p[5], (round(p[0]), round(p[1])), 3)
        self.text("COMMUNITY", cx - 44, cy + 18, 14, GOLD)
        self.text("One decision-maker controls the whole community. Figures are symbolic, not individual agents.", 36, 578, 14, MUTED)
        for index, (resource, color) in enumerate(RESOURCE_COLORS.items()):
            pygame.draw.circle(self.canvas, color, (48 + index * 145, 612), 5)
            self.text(resource.value.title(), 62 + index * 145, 600, 16)
        self.text("Observer sees all" if not self.fog else "Agent sight (radius 2)", 540, 600, 16, MUTED)
        self.draw_panel()
        self.draw_timeline(36, 642, 820)
        row = [
            ("Pause" if self.playing else "Play", 80, self.toggle_play, self.playing, self.controller != "manual" and not self.finished),
            ("Step", 66, self.single_step, False, self.controller != "manual" and not self.finished),
            (f"{self.speed:g}x speed", 96, self.change_speed, False, True),
            (self.controller.title(), 92, self.change_controller, False, True),
            (self.scenario.title(), 92, self.change_scenario, False, True),
            ("Sight", 66, self.toggle_fog, self.fog, True),
            ("Restart", 76, self.reset, False, True),
            ("New seed", 86, self.next_seed, False, True),
            ("Growth: " + ("On" if self.population_dynamics else "Off"), 100, self.toggle_population_dynamics, self.population_dynamics, self.controller != "rl"),
        ]
        x = 36
        for label, width, callback, active, enabled in row:
            self.button(label, (x, 667, width, 38), callback, active, enabled)
            x += width + 8
        self.text("Click the timeline to inspect a past turn. Play or Step resumes the live run; history is not rewound.", 36, 720, 14, MUTED)
        self.text("SPACE play/pause · N step · R restart | Manual: WASD move · 1/2/3 gather · 4/5/6/7 research · C conserve", 36, 750, 14, MUTED)
        if self.finished:
            self.text("RUN FINISHED — open Results to review", 36, 550, 18, GOLD)

    def draw_panel(self):
        pygame.draw.rect(self.canvas, PANEL, (887, 158, 357, 615), border_radius=16)
        state = self.displayed_state
        c = state.community
        self.text("LIVE" if self.inspection is None else "INSPECTING HISTORY", 910, 174, 18, GOLD)
        self.text(f"Turn {state.step} / {self.episode.scenario.world_config.max_steps}", 910, 201, 16, MUTED)
        self.text(f"{c.population:.1f} people", 910, 232, 28)
        record = self.displayed_record
        self.text(f"labour {c.available_labor:.1f}", 1090, 236, 14, MUTED)
        if self.population_dynamics and record:
            self.text(f"+{record['births']:.2f} born  -{record['starvation_deaths'] + record['natural_deaths']:.2f} died", 1090, 254, 14, GREEN if record['births'] else MUTED)
        action = self.displayed_record["action"] if self.displayed_record else "Initial state"
        self.text(action.replace(":", " · ").replace("_", " ").title(), 910, 274, 16, GREEN)
        for i, resource in enumerate(Resource):
            y = 310 + i * 30
            self.text(resource.value.title(), 910, y, 16, RESOURCE_COLORS[resource])
            self.text(f"{c.resources.amount(resource):.1f}", 1180, y, 16)
        self.text("TECHNOLOGY  (green = active)", 910, 411, 16, MUTED)
        for i, tid in enumerate(self.episode.instance.world.technology_graph.topological_ids()):
            y = 442 + i * 35
            p = c.technology(tid)
            progress = p.discovery_progress if p else 0
            self.text(tid.replace("_", " ").title(), 910, y, 16, GREEN if p and p.active else TEXT)
            self.text(f"{progress:.0%}", 1182, y, 14, MUTED)
            pygame.draw.rect(self.canvas, (38, 55, 65), (910, y + 24, 307, 4))
            pygame.draw.rect(self.canvas, GREEN if p and p.active else GOLD, (910, y + 24, int(307 * progress), 4))
        self.text("RECENT EVENTS" if self.inspection is None else "RECORDED CONSEQUENCE", 910, 596, 16, MUTED)
        events = self.events if self.inspection is None else self.wrap(turn_explanation(self.displayed_record), 307, 14)
        for i, event in enumerate(events):
            # Short log entries fit within the side panel; trim on very long IDs.
            self.text(event[:43], 910, 625 + i * 24, 14)

    def wrap(self, text, width, size=16):
        lines, line = [], ""
        for word in text.split():
            trial = f"{line} {word}".strip()
            if line and self.fonts[size].size(trial)[0] > width:
                lines.append(line)
                line = word
            else:
                line = trial
        return lines + ([line] if line else [])

    def paragraph(self, text, x, y, width, color=MUTED, size=16):
        for line in self.wrap(text, width, size):
            self.text(line, x, y, size, color)
            y += size + 8
        return y

    def draw_timeline(self, x, y, width):
        count = len(self.recording.turns)
        turn = self.displayed_state.step
        pygame.draw.line(self.canvas, MUTED, (x, y), (x + width, y), 3)
        px = x + width * turn / max(1, count)
        pygame.draw.circle(self.canvas, GOLD, (round(px), y), 7)
        rect = pygame.Rect(x - 8, y - 12, width + 16, 24)
        self.buttons.append((rect, lambda: self.inspect(round(max(0, min(1, (self.click_position[0] - x) / width)) * count))))
        self.text(f"Turn {turn} / {count} recorded", x, y - 24, 14, MUTED)

    def draw_results(self):
        summary = self.recording.summary(self.displayed_state.step)
        live = self.recording.summary()
        self.text(f"{summary['population_retained']:.1%} population retained", 36, 163, 28, GREEN if summary['population_retained'] == 1 else GOLD)
        self.text(f"{summary['population_lost']:.1f} people lost   |   {summary['shortage_turns']} shortage turns   |   {len(summary['discovered'])} discoveries", 36, 206, 18)
        first = summary['first_shortage'] if summary['first_shortage'] is not None else "none yet"
        self.text(f"{live['status'].upper()}  ·  {live['steps']} / {live['horizon']} turns run  ·  First shortage: {first}", 36, 238, 16, MUTED)
        if self.population_dynamics:
            self.text(f"Growth ON  ·  {summary['total_births']:.1f} born  ·  {summary['total_deaths']:.1f} died  ·  peak {summary['peak_population']:.1f}", 36, 258, 14, MUTED)
        graph = pygame.Rect(70, 294, 730, 190)
        pygame.draw.rect(self.canvas, PANEL, (36, 275, 820, 258), border_radius=12)
        initial = max(summary['initial_population'], *self.population_history)
        for fraction in (0, .5, 1):
            y = graph.bottom - fraction * graph.height
            pygame.draw.line(self.canvas, (43, 61, 73), (graph.left, y), (graph.right, y))
            self.text(f"{initial * fraction:g}", 43, y - 9, 14, MUTED)
        points = [(graph.x + i / live['horizon'] * graph.width, graph.bottom - p / initial * graph.height) for i, p in enumerate(self.population_history)]
        if len(points) > 1:
            pygame.draw.lines(self.canvas, GREEN, False, points, 3)
        for record in self.recording.turns:
            if record['shortage'] > 0:
                x = graph.x + record['step'] / live['horizon'] * graph.width
                pygame.draw.line(self.canvas, RED, (x, graph.bottom + 3), (x, graph.bottom + 8), 2)
        selected = summary['steps'] / live['horizon'] * graph.width + graph.x
        pygame.draw.line(self.canvas, GOLD, (selected, graph.top), (selected, graph.bottom), 1)
        self.buttons.append((graph, lambda: self.inspect(round((self.click_position[0] - graph.x) / graph.width * live['horizon']))))
        self.text("0", graph.left, 505, 14, MUTED)
        self.text("Population over turns", 350, 505, 14, MUTED)
        self.text(str(live['horizon']), graph.right - 25, 505, 14, MUTED)
        self.text("Red ticks = food shortages. Click the chart to inspect a recorded turn.", 36, 547, 14, MUTED)
        self.draw_timeline(36, 610, 820)
        self.button("Previous", (36, 638, 110, 36), lambda: self.inspect(self.displayed_state.step - 1))
        self.button("Next", (156, 638, 90, 36), lambda: self.inspect(self.displayed_state.step + 1))
        self.button("Live state", (256, 638, 110, 36), self.return_live, self.inspection is None)
        self.button("Compare baselines", (376, 638, 180, 36), self.compare)
        self.button("Export JSON / CSV", (566, 638, 180, 36), self.export_run)
        self.text("FULL-RUN REFERENCES  /  same scenario + seed", 36, 691, 16, GOLD)
        if self.comparisons:
            for i, result in enumerate(self.comparisons):
                self.text(f"{result['agent'].title()}: {result['trace'][-1]['population']:.1f} people after {result['steps']} turns", 36 + i * 405, 717, 16)
        else:
            self.text("Click Compare baselines to run two independent reference episodes.", 36, 717, 14, MUTED)
        self.text("Compare final outcomes only when your run finishes. One seed is not proof of general performance.", 36, 744, 14, MUTED)
        self.draw_turn_details()
        if self.notice:
            self.text(self.notice[:150], 36, 778, 14, GOLD)

    def draw_turn_details(self):
        pygame.draw.rect(self.canvas, PANEL, (887, 158, 357, 615), border_radius=16)
        record = self.displayed_record
        state = self.displayed_state
        self.text(f"TURN {state.step}: WHAT HAPPENED?", 910, 178, 18, GOLD)
        y = self.paragraph(turn_explanation(record), 910, 218, 310)
        self.text(f"Population: {state.community.population:.1f}", 910, y + 12, 18)
        if record:
            self.text(f"Food shortage: {record['shortage']:.2f}", 910, y + 42, 16, RED if record['shortage'] else MUTED)
            self.text("RESOURCE LEDGER", 910, 364, 16, GOLD)
            for i, resource in enumerate(Resource):
                name = resource.value
                delta = record['resource_changes'][name]
                self.text(f"{name.title()}: {state.community.resources.amount(resource):.2f}  ({delta:+.2f})", 910, 397 + i * 27, 16)
            self.text(f"Food eaten: {record['food_consumed']:.2f}", 910, 489, 14, MUTED)
            self.text(f"Travel / birth food: {record['movement_food_spent']:.2f} / {record.get('birth_food_spent', 0.0):.2f}", 910, 512, 14, MUTED)
            for label, key, y in (("Research paid", 'research_cost', 535), ("Maintenance", 'maintenance_paid', 558), ("Decay losses", 'decay_losses', 581)):
                values = record[key]
                self.text(f"{label} F/W/S: " + "/".join(f"{values[n]:.1f}" for n in ('food', 'wood', 'stone')), 910, y, 14, MUTED)
            self.text(f"Turn reward: {record['reward']:+.3f}", 910, 628, 16)
        self.paragraph("Reward is a training signal, not a win score. The ledger shows consequences; it does not explain the controller's intentions.", 910, 673, 310, size=14)

    def draw_guide(self):
        cards = [
            (36, 170, "1. WHAT AM I WATCHING?", "A single community moves on a grid, collects food, wood and stone, and researches technology. The people on screen symbolize population; they do not each make decisions. The world is generated from a seed."),
            (650, 170, "2. WHAT COUNTS AS A GOOD RESULT?", "First compare population retained at the end of the run. Then inspect shortages and technology discoveries. Reaching the time limit is not the same as preserving everyone. More technology is not automatically better: research uses turns and resources."),
            (36, 365, "3. WHY DO RESOURCES DISAPPEAR?", "Food supports population each turn. Moving also costs food. Research can require upfront food, wood and stone; active technologies may have upkeep. Resources also decay. Results shows the exact costs, gains and losses for each recorded turn."),
            (650, 365, "4. HOW DO I USE THE CONTROLS?", "Start with Rules and press Play or Step. Pause and open Results. Click the chart to inspect history. Compare baselines uses the same world and seed without touching your live run. Export saves the full recorded history, not just the selected turn."),
            (36, 560, "5. WHAT CAN THE CONTROLLER SEE?", "The default observer map reveals the whole world to you, but the controller only receives nearby deposits (radius 2). Sight hides distant resources. Changing scenario, controller or seed starts a new run and clears its history."),
            (650, 560, "6. WHERE DOES AI FIT?", "Rules and Random are comparison tools, not learning agents. RL requires a trained checkpoint; viewing it does not train it. Version 1 has four technologies: Fire leads to Cooking; Basic Tools leads to Storage. No language model is used here."),
        ]
        for x, y, title, body in cards:
            pygame.draw.rect(self.canvas, PANEL, (x, y, 594, 179), border_radius=12)
            self.text(title, x + 18, y + 14, 18, GOLD)
            self.paragraph(body, x + 18, y + 48, 555)
        self.text("Suggested first visit: Watch  →  Play  →  pause  →  Results  →  inspect a shortage  →  compare / export", 36, 760, 16, MUTED)

    def present(self):
        w, h = self.window.get_size()
        scale = min(w / WIDTH, h / HEIGHT)
        size = (max(1, int(WIDTH * scale)), max(1, int(HEIGHT * scale)))
        self.offset = ((w - size[0]) // 2, (h - size[1]) // 2)
        self.scale = scale
        self.window.fill(BG)
        self.window.blit(pygame.transform.smoothscale(self.canvas, size), self.offset)
        pygame.display.flip()

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = ((event.pos[0] - self.offset[0]) / self.scale, (event.pos[1] - self.offset[1]) / self.scale)
            self.click_position = pos
            for rect, callback in self.buttons:
                if rect.collidepoint(pos):
                    callback()
                    break
        if event.type != pygame.KEYDOWN:
            return
        if self.tab != "Watch":
            return
        if event.key == pygame.K_SPACE:
            self.toggle_play()
        elif event.key == pygame.K_n:
            self.playing = False
            self.step()
        elif event.key == pygame.K_r:
            self.reset()
        elif self.controller == "manual":
            mapping = {
                pygame.K_w: Action.move(Direction.NORTH), pygame.K_s: Action.move(Direction.SOUTH),
                pygame.K_a: Action.move(Direction.WEST), pygame.K_d: Action.move(Direction.EAST),
                pygame.K_1: Action.gather(Resource.FOOD), pygame.K_2: Action.gather(Resource.WOOD),
                pygame.K_3: Action.gather(Resource.STONE), pygame.K_c: Action.conserve(),
                pygame.K_4: Action.experiment("fire"), pygame.K_5: Action.experiment("cooking"),
                pygame.K_6: Action.experiment("basic_tools"), pygame.K_7: Action.experiment("storage"),
            }
            if event.key in mapping:
                self.step(self.episode.instance.world.action_catalog.encode(mapping[event.key]))

    def run(self):
        clock = pygame.time.Clock()
        self.draw()
        running = True
        while running:
            dt = min(clock.tick(60) / 1000, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                else:
                    self.handle(event)
            self.update(dt)
            self.draw()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("stable", "scarcity"), default="stable")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--controller", choices=("rules", "random", "manual", "rl"), default="rules")
    parser.add_argument("--checkpoint")
    parser.add_argument("--population-dynamics", action="store_true", help="Version 1.3: enable births, deaths and labour-scaled gathering.")
    parser.add_argument("--preview", help="Render a PNG preview and exit (for QA).")
    args = parser.parse_args()
    preview = args.preview
    del args.preview
    try:
        viewer = Viewer(**vars(args))
        if preview:
            for _ in range(8):
                viewer.step()
                viewer.update(0.1)
            viewer.draw()
            path = Path(preview)
            path.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(viewer.canvas, str(path))
        else:
            viewer.run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
