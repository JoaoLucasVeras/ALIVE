"""Paired-seed evaluation with raw metrics, replay records, and an HTML report."""

import argparse
import csv
import html
import json
from pathlib import Path
from statistics import mean, stdev
from .baseline_agents import RandomAgent, RuleAgent
from .environment.episode import Episode, run_episode
from .environment.scenarios import scenario_by_name


def evaluate(scenario="stable", episodes=20, seed_start=10000,
             checkpoint=None, output="results/evaluation",
             technology_ablation=False):
    if episodes < 1 or seed_start < 0:
        raise ValueError("episodes must be positive and seeds non-negative")
    definition = scenario_by_name(scenario)
    agents = {"random": RandomAgent(), "rules": RuleAgent()}
    if technology_ablation:
        agents["rules_no_research"] = RuleAgent(research_enabled=False)
    if checkpoint:
        import torch
        torch.set_num_threads(1)
        from .rl_policy import PolicyAgent
        payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
        first, last = payload["training_seeds"]
        if max(first, seed_start) <= min(last, seed_start + episodes - 1):
            raise ValueError("evaluation seeds overlap training seeds")
        agents["rl"] = PolicyAgent(checkpoint, Episode(definition))
    path = Path(output)
    path.mkdir(parents=True, exist_ok=True)
    run_path = path / "runs"
    run_path.mkdir(exist_ok=True)
    configuration = {
        "scenario": scenario,
        "episodes": episodes,
        "seed_start": seed_start,
        "seeds": list(range(seed_start, seed_start + episodes)),
        "checkpoint": checkpoint,
        "technology_ablation": technology_ablation,
        "agents": list(agents),
    }
    (path / "configuration.json").write_text(
        json.dumps(configuration, indent=2), encoding="utf-8"
    )
    rows, summaries = [], []
    for name, agent in agents.items():
        runs = []
        for seed in range(seed_start, seed_start + episodes):
            complete_result = run_episode(agent, definition, seed)
            (run_path / f"{name}_seed_{seed}.json").write_text(
                json.dumps(complete_result, indent=2), encoding="utf-8"
            )
            result = {key: value for key, value in complete_result.items() if key != "trace"}
            trace = complete_result["trace"]
            # Fixed seed selection avoids choosing only attractive replays.
            if seed == seed_start:
                (path / f"replay_{name}.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
            result["agent"] = name
            rows.append(result)
            runs.append(result)
        values = [r["population_retained"] for r in runs]
        summaries.append({"agent": name, "mean_population_retained": mean(values),
                          "population_std": stdev(values) if len(values) > 1 else 0.0,
                          "mean_return": mean(r["return"] for r in runs),
                          "mean_shortage": mean(r["shortage_total"] for r in runs),
                          "mean_discovered": mean(len(r["discovered"]) for r in runs)})
    (path / "summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    with (path / "episodes.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    comparison = None
    if technology_ablation:
        by_agent_seed = {(row["agent"], row["seed"]): row for row in rows}
        pairs = []
        for seed in range(seed_start, seed_start + episodes):
            enabled = by_agent_seed[("rules", seed)]
            disabled = by_agent_seed[("rules_no_research", seed)]
            pairs.append({
                "seed": seed,
                "enabled_population_retained": enabled["population_retained"],
                "disabled_population_retained": disabled["population_retained"],
                "population_retained_delta": (
                    enabled["population_retained"] - disabled["population_retained"]
                ),
                "enabled_shortage": enabled["shortage_total"],
                "disabled_shortage": disabled["shortage_total"],
                "shortage_delta": enabled["shortage_total"] - disabled["shortage_total"],
                "enabled_return": enabled["return"],
                "disabled_return": disabled["return"],
                "return_delta": enabled["return"] - disabled["return"],
                "enabled_discovered": enabled["discovered"],
                "disabled_discovered": disabled["discovered"],
            })
        comparison = {
            "question": "Does allowing the same rule policy to research technology change outcomes?",
            "enabled_agent": "rules",
            "restricted_agent": "rules_no_research",
            "mean_population_retained_delta": mean(
                pair["population_retained_delta"] for pair in pairs
            ),
            "mean_shortage_delta": mean(pair["shortage_delta"] for pair in pairs),
            "mean_return_delta": mean(pair["return_delta"] for pair in pairs),
            "enabled_population_wins": sum(
                pair["population_retained_delta"] > 0 for pair in pairs
            ),
            "restricted_population_wins": sum(
                pair["population_retained_delta"] < 0 for pair in pairs
            ),
            "population_ties": sum(
                pair["population_retained_delta"] == 0 for pair in pairs
            ),
            "pairs": pairs,
        }
        (path / "technology_comparison.json").write_text(
            json.dumps(comparison, indent=2), encoding="utf-8"
        )
    bars = "".join(f'<p>{html.escape(r["agent"])}: {r["mean_population_retained"]:.1%} population retained</p><meter min="0" max="1" value="{r["mean_population_retained"]}"></meter>' for r in summaries)
    comparison_html = ""
    if comparison:
        comparison_html = (
            "<h2>Technology ablation</h2>"
            f'<p>Mean paired population-retention difference (enabled minus restricted): '
            f'{comparison["mean_population_retained_delta"]:+.1%}. '
            f'Enabled wins: {comparison["enabled_population_wins"]}; '
            f'restricted wins: {comparison["restricted_population_wins"]}; '
            f'ties: {comparison["population_ties"]}.</p>'
        )
    (path / "report.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>ALIVE evaluation</title><style>body{font:18px system-ui;max-width:800px;margin:40px auto;padding:20px}meter{width:100%;height:30px}</style>' +
        f'<h1>ALIVE — {html.escape(scenario)}</h1><p>{episodes} paired seeds starting at {seed_start}. Bars show final population divided by starting population; they are measured results.</p>' + bars +
        comparison_html + '<p>See episodes.csv, summary.json, configuration.json, runs/, and technology_comparison.json when enabled. Replays use the first evaluation seed.</p></html>', encoding="utf-8")
    print(json.dumps(summaries, indent=2))
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("stable", "scarcity"), default="stable")
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--seed-start", type=int, default=10000)
    parser.add_argument("--checkpoint")
    parser.add_argument("--output", default="results/evaluation")
    parser.add_argument(
        "--technology-ablation",
        action="store_true",
        help="compare the rule policy with research enabled versus disabled",
    )
    evaluate(**vars(parser.parse_args()))


if __name__ == "__main__":
    main()
