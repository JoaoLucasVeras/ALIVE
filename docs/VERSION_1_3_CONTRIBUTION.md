# Version 1.3: population dynamics (births, deaths, labour)

## Release naming

| Version | What it is | Owner |
| --- | --- | --- |
| 1 | Shared simulation foundation: one community, three resources, four technologies, baselines, RL | Team |
| 1.2 | Research-strategy comparison (none / fire / cooking / all) | Akshay |
| 1.3 | Population dynamics: births, natural deaths, labour-scaled gathering | Aryan |

Historical archives, evidence files and old file names keep their original identifiers.

## What is new

Before 1.3, population could only fall (starvation) and labour was a fixed fraction that affected nothing. Version 1.3 makes population a real mechanic. It is **opt-in** (`ResolverConfig.with_population_dynamics()`), so Version 1 and 1.2 behaviour and traces are unchanged (the existing trace-hash test still passes).

- **Births.** On any turn without a food shortage: `births = population x 0.03 x (1 - population / 120)`, limited to food above a 0.2 food/person reserve. Each birth costs 1 food.
- **Natural deaths.** 0.2% of the population per turn, in addition to starvation deaths.
- **Labour.** Gathering is multiplied by `sqrt(labour / starting labour)`, capped at 2x.
- **Ledger.** Birth food is tracked (`birth_food_spent`) and the per-turn food ledger still reconciles exactly.

Changed files: `environment/resolver.py` (mechanic), `environment/episode.py` (trace fields, only when enabled), `viewer.py` (Growth toggle, labour and births display, `--population-dynamics`), `viewer_results.py` (summary, CSV, same-rule reference runs). Tests: `tests/test_population.py`, plus a viewer test.

## Viewer

The **Growth: On/Off** button restarts the same scenario and seed. Reference runs ("Compare baselines") use the same rules as the live run, and exports record `population_dynamics` and the full resolver settings. Growth is unavailable for the RL controller because checkpoints were trained without it.

## Measured effect (rule agent, seeds 20000-20019, 20 episodes)

| Scenario | Growth | Mean retained | Collapsed | Mean peak population |
| --- | --- | --- | --- | --- |
| stable | off | 47.4% | 0/20 | 40.0 |
| stable | on | 32.5% | 5/20 | 45.8 |
| scarcity | off | 20.2% | 0/20 | 40.0 |
| scarcity | on | 19.6% | 0/20 | 43.9 |

**Interpretation, honestly:** the existing rule agent is not growth-aware, so growth adds boom-and-bust risk and, on stable, lowers retention. This is a finding, not a tuned success: the preset was chosen from a small parameter sweep and not optimised. Population "retained" can now exceed 100% in principle. The RL observation caps population at the starting value, so a learned agent cannot see growth above 1.0.

## Growth-aware reference agent

`GrowthAwareRuleAgent` (`baseline_agents.py`) holds a larger food buffer and starts research later. It cannot see growth directly, since the observation caps population at its starting value. Run `python -m alive.evaluate --population-dynamics` to compare it with the plain rule agent under growth. Mean population retained under growth (20 episodes each, growth on):

| Seeds | Scenario | Plain rules | Growth-aware | Collapses (plain / aware) |
| --- | --- | --- | --- | --- |
| 20000-20019 (used while tuning) | stable | 32.5% | 36.2% | 5 / 3 |
| 20000-20019 (used while tuning) | scarcity | 19.6% | 20.1% | 0 / 0 |
| 30000-30019 (held out) | stable | 27.8% | 34.6% | 2 / 1 |
| 30000-30019 (held out) | scarcity | 16.3% | 17.0% | 2 / 0 |

It helps modestly but does not recover Version 1 retention (47.4% stable with growth off). Differences are small and from 20 seeds each, so treat them as indicative, not proven.

## Verification

34 tests run, 32 pass and 2 are skipped (RL/torch not installed). The viewer tests ran with pygame-ce. Checked: defaults reproduce Version 1/1.2 traces; births respect the cap and need no shortage; population change equals births minus deaths each turn; the food ledger reconciles; labour is bounded; viewer runs match headless runs; exports carry the settings.

## Not done / limits

No RL retraining or growth-aware RL policy, no multi-seed confidence intervals, and one parameter preset only. The next planned feature (stockpile and spoilage) builds on this one.
