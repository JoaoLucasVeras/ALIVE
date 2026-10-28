# ALIVE
Adaptive Life in Virtual Environments: a simulation where virtual communities learn survival and technology strategies through reinforcement learning.

**Versions.** Version 1 is the shared simulation foundation. Version 1.2 (Akshay) adds research-strategy comparison. Version 1.3 (Aryan) adds population dynamics: births, deaths and labour-scaled gathering.

Version 1 implements one community, three resources, four technologies, stable and scarcity worlds, random and rule-based baselines, and a masked recurrent PPO learner. Multiple communities, trading, sharing, scheduled environmental shocks, and LLM assistance belong to later levels.

## Project handbook · start here

The [central handbook](docs/PROJECT_HANDBOOK.md) explains the vision, actual implementation, architecture, proposed roadmap, work queue, development journal, research, and open decisions. It separates working features from proposals and evidence of learning from infrastructure tests.

Open [the standalone offline website](docs/handbook/ALIVE_Handbook.html) in a browser, or share that single HTML file with a teammate/advisor. It includes search, navigation, task-priority filters, Markdown download, and whole-handbook printing. For local HTTP preview, run `powershell -ExecutionPolicy Bypass -File .\Start_ALIVE_Handbook.ps1`. See [maintenance instructions](docs/handbook/README.md). This edition is local and has not been deployed publicly.

## Setup

Use Python 3.11 or newer from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
python -m alive.evaluate --episodes 20 --output results/baselines
```

For RL, install the optional dependencies:

```powershell
python -m pip install -e ".[rl]"
python -m alive.train --updates 2 --episodes-per-update 2 --epochs 2 --output results/smoke
python -m alive.evaluate --checkpoint results/smoke/policy.pt --episodes 5 --output results/smoke_eval
```

The short run verifies training and checkpoint loading; it does not establish learning quality. A larger run:

```powershell
python -m alive.train --updates 100 --episodes-per-update 4 --output results/training
python -m alive.evaluate --checkpoint results/training/policy.pt --episodes 20 --seed-start 10000
python -m alive.evaluate --scenario scarcity --episodes 20 --output results/scarcity_baselines
```

CPU is the default. Use `--device cuda` only with a CUDA-enabled PyTorch installation. This reference trainer runs worlds sequentially; a GPU may not make a small run faster. Evaluation rejects training-seed overlap and incompatible checkpoint configurations. Train a separate scarcity model to evaluate that preset; cross-scenario transfer is a later explicit experiment.

Evaluation creates `episodes.csv`, `summary.json`, `report.html`, and first-seed replay JSON files. Training creates `configuration.json`, `learning_curve.csv`, and `policy.pt`. Open `report.html` in a browser for the measured population comparison. Results are ignored by Git.

To test whether technology changes outcomes for the rule strategy, run a paired ablation. It compares identical seeds with research enabled and disabled, writes every full trace under `runs/`, and adds `technology_comparison.json`:

```powershell
python -m alive.evaluate --scenario stable --episodes 20 --seed-start 0 --technology-ablation --output results/technology_value_stable
```

This measures the combined cost and benefit of choosing research under the same environment. It does not isolate individual technology effects or prove causality for RL behavior.

### Compare research strategies

Choose the rule policy's research path with `--research-strategy none|fire|cooking|all`.
`cooking` researches Fire first, then Cooking. `all` preserves the default behavior.
These options restrict policy choices; the technology graph and simulation rules stay the same.

```bash
# Run from the repository root with the virtual environment active.
python -m alive.evaluate --research-strategy fire --episodes 20 --output results/fire_only
python -m alive.evaluate --compare-research-strategies --episodes 20 --seed-start 0 --output results/research_strategies
```

Comparison mode evaluates all four research paths plus Random on identical seeds.
It records the selected paths in `configuration.json`, each full run, `episodes.csv`,
and `summary.json`. `research_comparison.json` contains per-seed population,
shortage, and return differences against no research, with win/loss/tie counts.
Open `report.html` for retention, variance, shortages, returns, discoveries, and paired comparisons.
Use a fresh output directory for each experiment to avoid mixing artifacts from older runs.

Comparison mode and `--technology-ablation` are mutually exclusive. Neither accepts
a non-default `--research-strategy`. RL checkpoint evaluation remains available;
the strategy option applies only to Rules. The native viewer continues using its default rule policy.
These are complete strategy comparisons, not isolated technology effects or evidence of RL learning.

The [design specification](docs/Research_Strategy_Design_Spec.docx) describes the implementation,
TDD evidence, and measured stable-seed results. Run the feature tests with
`python -m unittest discover -s tests -p test_research_strategies.py -v`.

See [the file-by-file guide](docs/LEVEL_1_GUIDE.md) for mechanics, contracts, limitations, and the learning loop.

## Game-style local viewer

The native viewer animates the real simulation on an isometric map. It needs no GPU or RL packages to run the baseline agents.

```powershell
python -m pip install -e ".[viewer]"
python -m alive.viewer
```

Alternatively, from PowerShell in the project directory run `powershell -ExecutionPolicy Bypass -File .\Start_ALIVE_Viewer.ps1`. The launcher creates an isolated `.venv-viewer` on first use, installs the viewer dependency, and opens the window. It requires Python 3.11+ available as `python`; supply `-Python 'C:\path\to\python.exe'` for a different installation. Initial dependency installation needs internet access. The execution-policy override applies only to that invocation.

The window starts paused. Click **Play** or press **Space**. **N** advances one turn; **R** restarts the same seed. Buttons select speed, controller, stable/scarcity scenario, agent sight, restart, and the next seed. Changing controller/scenario resets the episode. The observer map reveals deposits for the human viewer; both baseline and RL decisions still use only local observations.

Three tabs make the run easier to interpret: **Watch** shows the world, **Results** shows population retention, shortage markers, inspectable turn history, and resource accounting, and **Guide** explains the goal and mechanics. Results can run same-seed Rules/Random references and export the current recording to JSON and CSV under `results/viewer_runs/`. Inspecting history pauses playback without rewinding the live episode. Baseline references are complete runs; compare them with your run only after it finishes.

Switch to **Manual** to play directly: **WASD** moves, **1/2/3** gathers food/wood/stone, **4/5/6/7** researches Fire/Cooking/Basic Tools/Storage, and **C** conserves. Illegal actions are rejected without advancing time. **Esc** closes the window.

```powershell
python -m alive.viewer --scenario scarcity --seed 7 --controller random
# Optional RL playback; requires both .[viewer] and .[rl]:
python -m alive.viewer --controller rl --checkpoint results/ppo_smoke/policy.pt
```

The settlers represent one aggregate community, not individually simulated people. Animated legs, resource particles and research pulses are presentation effects; movement and resource outcomes come from the actual engine. The current population balance can still lead to decline or collapse. See [the viewer guide](docs/VIEWER_GUIDE.md).

## Version 1.3: population dynamics

Opt-in, off by default so Version 1 and 1.2 results are unchanged. Enable it with `ResolverConfig.with_population_dynamics()`, or in the viewer:

```powershell
python -m alive.viewer --population-dynamics
```

or click **Growth: On/Off** on the Watch tab (restarts the same scenario and seed). Rules: each turn without a food shortage, births = population x 3% x (1 - population/120), limited by food above a 0.2 food/person reserve, each birth costing 1 food; natural deaths remove 0.2% per turn; starvation deaths work as before; gathering scales with the square root of labour relative to the starting workforce (capped at 2x). Reference runs and exports use the same rules. RL checkpoints were trained without growth, so Growth is unavailable with the RL controller. See [the Version 1.3 contribution record](docs/VERSION_1_3_CONTRIBUTION.md).
