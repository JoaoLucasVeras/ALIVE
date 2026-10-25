"""Masked recurrent actor-critic and versioned checkpoint contract."""

import torch
from torch import nn
from torch.distributions import Categorical


class RecurrentPolicy(nn.Module):
    def __init__(self, input_size, action_count, hidden_size=128):
        super().__init__()
        self.hidden_size = hidden_size
        self.encoder = nn.Sequential(nn.Linear(input_size, hidden_size), nn.Tanh())
        self.memory = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.actor = nn.Linear(hidden_size, action_count)
        self.critic = nn.Linear(hidden_size, 1)

    def forward(self, observations, masks, hidden=None):
        encoded = self.encoder(observations)
        output, hidden = self.memory(encoded, hidden)
        logits = self.actor(output).masked_fill(~masks.bool(), -1e9)
        return Categorical(logits=logits), self.critic(output).squeeze(-1), hidden


def interface_contract(episode, observation):
    """Include mechanics as well as observation/action ordering in checkpoints."""
    from dataclasses import asdict
    import json
    contract = {
        "version": 1, "feature_names": list(observation.names),
        "action_labels": list(episode.instance.world.action_catalog.labels),
        "world_config": asdict(episode.scenario.world_config),
        "technology_graph": asdict(episode.instance.world.technology_graph),
        "resolver": asdict(episode.resolver.config),
        "reward": asdict(episode.reward_config),
        "scenario": asdict(episode.scenario),
    }
    # Save plain primitives only: safe weights-only loading rejects enum classes.
    return json.loads(json.dumps(contract, default=lambda x: sorted(x) if isinstance(x, frozenset) else str(x)))


class PolicyAgent:
    def __init__(self, checkpoint, episode, deterministic=True, device="cpu"):
        self.device = torch.device(device)
        payload = torch.load(checkpoint, map_location=self.device, weights_only=True)
        observation = episode.reset(0)
        if payload["contract"] != interface_contract(episode, observation):
            raise ValueError("checkpoint configuration differs from this environment")
        self.policy = RecurrentPolicy(len(observation.values), len(observation.action_mask), payload["hidden_size"]).to(self.device)
        self.policy.load_state_dict(payload["weights"])
        self.policy.eval()
        self.deterministic = deterministic

    def reset(self, seed):
        self.hidden = None
        torch.manual_seed(seed + 2_000_000)

    @torch.no_grad()
    def act(self, observation):
        x = torch.tensor(observation.values, dtype=torch.float32, device=self.device)[None, None]
        mask = torch.tensor(observation.action_mask, device=self.device)[None, None]
        distribution, _, self.hidden = self.policy(x, mask, self.hidden)
        action = distribution.probs.argmax(-1) if self.deterministic else distribution.sample()
        return int(action.item())
