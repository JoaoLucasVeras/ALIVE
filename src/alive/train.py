"""Small recurrent PPO trainer using complete episodes and full sequences.

Sequence order is preserved when recomputing recurrent states. This reference
trainer favors inspectability; vectorized rollouts are a later optimization.
"""

import argparse
import csv
import json
from pathlib import Path
import torch
from .environment.episode import Episode
from .environment.scenarios import scenario_by_name
from .rl_policy import RecurrentPolicy, interface_contract


def advantages(rewards, values, bootstrap, gamma=0.99, lam=0.95):
    result = [0.0] * len(rewards)
    carry, next_value = 0.0, bootstrap
    for t in range(len(rewards) - 1, -1, -1):
        carry = rewards[t] + gamma * next_value - values[t] + gamma * lam * carry
        result[t] = carry
        next_value = values[t]
    return result, [a + v for a, v in zip(result, values)]


def train(updates=100, episodes_per_update=4, epochs=4, seed=0,
          scenario="stable", output="results/training", device="cpu", hidden_size=128):
    if min(updates, episodes_per_update, epochs, hidden_size) < 1 or seed < 0:
        raise ValueError("counts must be positive and seed non-negative")
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    device = torch.device(device)
    episode = Episode(scenario_by_name(scenario))
    obs = episode.reset(seed)
    contract = interface_contract(episode, obs)
    policy = RecurrentPolicy(len(obs.values), len(obs.action_mask), hidden_size).to(device)
    optimizer = torch.optim.Adam(policy.parameters(), lr=3e-4)
    path = Path(output)
    path.mkdir(parents=True, exist_ok=True)
    settings = dict(updates=updates, episodes_per_update=episodes_per_update,
                    epochs=epochs, seed=seed, scenario=scenario, device=str(device))
    (path / "configuration.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    history = []
    for update in range(updates):
        trajectories, returns, retained = [], [], []
        for number in range(episodes_per_update):
            obs = episode.reset(seed + update * episodes_per_update + number)
            hidden = None
            xs, masks, acts, logps, vals, rewards = [], [], [], [], [], []
            while True:
                x = torch.tensor(obs.values, dtype=torch.float32, device=device)[None, None]
                mask = torch.tensor(obs.action_mask, device=device)[None, None]
                with torch.no_grad():
                    dist, value, hidden = policy(x, mask, hidden)
                    action = dist.sample()
                xs.append(obs.values)
                masks.append(obs.action_mask)
                acts.append(int(action.item()))
                logps.append(float(dist.log_prob(action).item()))
                vals.append(float(value.item()))
                obs, reward, terminated, truncated, _ = episode.step(acts[-1])
                rewards.append(reward)
                if terminated or truncated:
                    # Time-limit truncation bootstraps; true population collapse does not.
                    bootstrap = 0.0
                    if truncated:
                        with torch.no_grad():
                            _, v, _ = policy(torch.tensor(obs.values, dtype=torch.float32, device=device)[None, None],
                                             torch.tensor(obs.action_mask, device=device)[None, None], hidden)
                            bootstrap = float(v.item())
                    break
            adv, targets = advantages(rewards, vals, bootstrap)
            trajectories.append((xs, masks, acts, logps, adv, targets))
            returns.append(sum(rewards))
            retained.append(episode.state.community.population / episode.scenario.world_config.starting_population)
        all_adv = torch.tensor([a for t in trajectories for a in t[4]], device=device)
        mean, std = all_adv.mean(), all_adv.std(unbiased=False).clamp_min(1e-8)
        total_steps = len(all_adv)
        for _ in range(epochs):
            optimizer.zero_grad()
            for xs, masks, acts, logps, adv, targets in trajectories:
                x = torch.tensor(xs, dtype=torch.float32, device=device)[None]
                mask = torch.tensor(masks, device=device)[None]
                dist, value, _ = policy(x, mask)  # Reset GRU at episode boundary.
                action = torch.tensor(acts, device=device)[None]
                old = torch.tensor(logps, device=device)[None]
                advantage = (torch.tensor(adv, device=device)[None] - mean) / std
                target = torch.tensor(targets, device=device)[None]
                ratio = (dist.log_prob(action) - old).exp()
                actor = -torch.minimum(ratio * advantage, ratio.clamp(0.8, 1.2) * advantage).mean()
                loss = actor + 0.5 * (value - target).square().mean() - 0.01 * dist.entropy().mean()
                if not torch.isfinite(loss):
                    raise RuntimeError("non-finite PPO loss")
                (loss * len(xs) / total_steps).backward()
            torch.nn.utils.clip_grad_norm_(policy.parameters(), 0.5)
            optimizer.step()
        row = dict(update=update + 1, mean_return=sum(returns)/len(returns),
                   mean_population_retained=sum(retained)/len(retained), steps=total_steps)
        history.append(row)
        print(json.dumps(row), flush=True)
    with (path / "learning_curve.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)
    torch.save(dict(weights=policy.state_dict(), hidden_size=hidden_size,
                    contract=contract, training=settings,
                    training_seeds=[seed, seed + updates * episodes_per_update - 1]), path / "policy.pt")
    return policy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--updates", type=int, default=100)
    parser.add_argument("--episodes-per-update", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--scenario", choices=("stable", "scarcity"), default="stable")
    parser.add_argument("--output", default="results/training")
    parser.add_argument("--device", default="cpu")
    train(**vars(parser.parse_args()))


if __name__ == "__main__":
    main()
