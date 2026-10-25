"""Gymnasium adapter; install the optional 'rl' dependencies to import."""

import gymnasium as gym
import numpy as np
from .episode import Episode
from .scenarios import scenario_by_name


class AliveEnv(gym.Env):
    metadata = {"render_modes": ["ansi"]}

    def __init__(self, scenario="stable", render_mode=None):
        self.episode = Episode(scenario_by_name(scenario))
        initial = self.episode.reset(0)
        self.action_space = gym.spaces.Discrete(len(initial.action_mask))
        self.observation_space = gym.spaces.Box(0, 1, (len(initial.values),), dtype=np.float32)
        if render_mode not in (None, "ansi"):
            raise ValueError("supported render mode: ansi")
        self.render_mode = render_mode

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        episode_seed = seed if seed is not None else int(self.np_random.integers(0, 2**31))
        obs = self.episode.reset(episode_seed)
        return np.asarray(obs.values, dtype=np.float32), {"action_mask": np.asarray(obs.action_mask)}

    def step(self, action):
        obs, reward, terminated, truncated, info = self.episode.step(int(action))
        info["action_mask"] = np.asarray(obs.action_mask)
        return np.asarray(obs.values, dtype=np.float32), reward, terminated, truncated, info

    def action_masks(self):
        from .observations import observe
        return np.asarray(observe(self.episode.instance.world, self.episode.state).action_mask)

    def render(self):
        c = self.episode.state.community
        return f"step={self.episode.state.step} position={c.position} population={c.population:.2f} resources={c.resources}"
