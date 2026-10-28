"""Paired-seed evaluation with raw metrics, replay records, and an HTML report."""

import argparse
import csv
import html
import json
from pathlib import Path
from statistics import mean, stdev
from .baseline_agents import RandomAgent, RuleAgent, RESEARCH_STRATEGIES
from .environment.episode import Episode, run_episode
from .environment.scenarios import scenario_by_name


def evaluate(scenario="stable", episodes=20, seed_start=10000,
             checkpoint=None, output="results/evaluation",
             technology_ablation=False, research_strategy="all",
             compare_research_strategies=False):
    if episodes < 1 or seed_start < 0:
        raise ValueError("episodes must be positive and seeds non-negative")
    if research_strategy not in RESEARCH_STRATEGIES:
        raise ValueError(f"unknown research strategy: {research_strategy!r}")
    if (technology_ablation and compare_research_strategies or
            research_strategy != "all" and (technology_ablation or compare_research_strategies)):
        raise ValueError("choose one research strategy, technology ablation, or strategy comparison")
    definition = scenario_by_name(scenario)
    agents = {"random": RandomAgent(), "rules": RuleAgent(research_strategy=research_strategy)}
    if compare_research_strategies:
        agents = {"random": RandomAgent(), **{
            f"rules_{strategy}": RuleAgent(research_strategy=strategy)
            for strategy in RESEARCH_STRATEGIES
        }}
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
        "compare_research_strategies": compare_research_strategies,
        "research_strategies": {name: agent.research_strategy for name, agent in agents.items()
                                if isinstance(agent, RuleAgent)},
    }
    (path / "configuration.json").write_text(
        json.dumps(configuration, indent=2), encoding="utf-8"
    )
    rows, summaries = [], []
    for name, agent in agents.items():
        runs = []
        for seed in range(seed_start, seed_start + episodes):
            complete_result = run_episode(agent, definition, seed)
            complete_result["research_strategy"] = configuration["research_strategies"].get(name)
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
        summaries.append({"agent": name,
                          "research_strategy": configuration["research_strategies"].get(name),
                          "mean_population_retained": mean(values),
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
    metrics_html = '<h2>Outcome metrics</h2><table><tr><th>Controller</th><th>Retention SD</th><th>Mean shortage</th><th>Mean return</th><th>Mean discoveries</th></tr>'
    for row in summaries:
        metrics_html += (f'<tr><td>{html.escape(row["agent"])}</td><td>{row["population_std"]:.2%}</td>'
                         f'<td>{row["mean_shortage"]:.2f}</td><td>{row["mean_return"]:.2f}</td>'
                         f'<td>{row["mean_discovered"]:.2f}</td></tr>')
    metrics_html += '</table><p>Retention SD is the sample standard deviation across world seeds; it is not a confidence interval.</p>'
    comparison_html = ""
    if compare_research_strategies:
        strategy_comparison = compare_strategies(rows)
        (path / "research_comparison.json").write_text(
            json.dumps(strategy_comparison, indent=2), encoding="utf-8")
        comparison_html = '<h2>Research strategy comparison</h2><p>Differences are paired against no research. These compare complete rule strategies, not isolated technology effects or RL learning.</p>'
        comparison_html += '<table><tr><th>Strategy</th><th>Mean retention difference</th><th>Wins / losses / ties</th></tr>'
        for item in strategy_comparison["comparisons"]:
            comparison_html += (f'<tr><td>{html.escape(item["agent"])}</td>'
                                f'<td>{item["mean_population_retained_delta"]:+.2%}</td>'
                                f'<td>{item["wins"]} / {item["losses"]} / {item["ties"]}</td></tr>')
        comparison_html += '</table><p>See research_comparison.json for every paired difference.</p>'
    if comparison:
        comparison_html = (
            "<h2>Technology ablation</h2>"
            f'<p>Mean paired population-retention difference (enabled minus restricted): '
            f'{comparison["mean_population_retained_delta"]:+.1%}. '
            f'Enabled wins: {comparison["enabled_population_wins"]}; '
            f'restricted wins: {comparison["restricted_population_wins"]}; '
            f'ties: {comparison["population_ties"]}.</p>'
        )
    (path / "report.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>ALIVE evaluation</title><style>body{font:18px system-ui;max-width:900px;margin:40px auto;padding:20px}meter{width:100%;height:30px}table{width:100%;border-collapse:collapse;font-size:15px}th,td{text-align:left;padding:10px;border-bottom:1px solid #ddd}</style>' +
        f'<h1>ALIVE — {html.escape(scenario)}</h1><p>{episodes} paired seeds starting at {seed_start}. Bars show final population divided by starting population; they are measured results.</p>' + bars +
        metrics_html + comparison_html + '<p>See episodes.csv, summary.json, configuration.json, runs/, and technology_comparison.json when enabled. Replays use the first evaluation seed.</p></html>', encoding="utf-8")
    print(json.dumps(summaries, indent=2))
    return summaries


def compare_strategies(rows):
    """Pair every research strategy with the same-seed no-research reference."""
    by_agent_seed = {(row["agent"], row["seed"]): row for row in rows}
    seeds = sorted({row["seed"] for row in rows})
    comparisons = []
    for strategy in RESEARCH_STRATEGIES:
        if strategy == "none":
            continue
        name = f"rules_{strategy}"
        pairs = []
        for seed in seeds:
            candidate = by_agent_seed[name, seed]
            reference = by_agent_seed["rules_none", seed]
            pairs.append({"seed": seed,
                          "population_retained_delta": candidate["population_retained"] - reference["population_retained"],
                          "shortage_delta": candidate["shortage_total"] - reference["shortage_total"],
                          "return_delta": candidate["return"] - reference["return"]})
        comparisons.append({"agent": name,
                            **{f"mean_{key}": mean(pair[key] for pair in pairs)
                               for key in ("population_retained_delta", "shortage_delta", "return_delta")},
                            "wins": sum(pair["population_retained_delta"] > 0 for pair in pairs),
                            "losses": sum(pair["population_retained_delta"] < 0 for pair in pairs),
                            "ties": sum(pair["population_retained_delta"] == 0 for pair in pairs),
                            "pairs": pairs})
    return {"reference_agent": "rules_none", "comparisons": comparisons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("stable", "scarcity"), default="stable")
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--seed-start", type=int, default=10000)
    parser.add_argument("--checkpoint")
    parser.add_argument("--output", default="results/evaluation")
    parser.add_argument("--research-strategy", choices=tuple(RESEARCH_STRATEGIES), default="all",
                        help="rule-policy research path; cooking includes its Fire prerequisite")
    parser.add_argument("--compare-research-strategies", action="store_true",
                        help="compare none, fire, cooking and all on identical seeds, plus Random")
    parser.add_argument(
        "--technology-ablation",
        action="store_true",
        help="compare the rule policy with research enabled versus disabled",
    )
    evaluate(**vars(parser.parse_args()))


if __name__ == "__main__":
    main()
