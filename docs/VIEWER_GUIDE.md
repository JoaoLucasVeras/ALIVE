# ALIVE local viewer

Run `python -m pip install -e ".[viewer]"` followed by `python -m alive.viewer` from the repository root, using the virtual environment described in README.md. The viewer runs locally as a desktop window and works with CPU graphics. RL dependencies are optional unless you load an RL checkpoint.

## What you will see

The viewer has three tabs: **Watch** for the animated world, **Results** for recorded outcomes, and **Guide** for a first-time explanation. Switching tabs pauses playback. The mission banner states the primary objective: preserve the starting population through the episode's time limit. This is an interpretation of the existing survival objective, not a new success rule or a change to rewards.

- An isometric grid with warm-colored food crops, green trees for wood, and gray stone deposits.
- Small animated settlers moving smoothly between actual grid positions. Their count broadly tracks aggregate population, rather than simulating individuals.
- Resource particles when gathering and a research ring when experimenting.
- A side panel showing the current action, population, inventories, discovery progress, and recent events.
- A full observer map by default; Sight switches to the agent's current radius-two neighborhood. Agent controllers always receive the same limited observations regardless of this setting.

This is a first visual interpretation of the project, with code-drawn art. Grass colors and animation use a separate cosmetic clock/random stream; they cannot alter episode randomness or outcomes. There are no settlement buildings or individually simulated human behaviors yet.

## Controls

| Control | Behavior |
|---|---|
| Play / Space | Start or pause automatic decisions. Starts paused. |
| Step / N | Advance one automatic action. |
| Speed | Cycle 0.5x, 1x, 2x, 4x. Changes presentation timing only. |
| Controller | Cycle rules, random, manual, and RL if a checkpoint was supplied. Resets the episode. |
| Scenario | Switch stable/scarcity and reset. A loaded RL policy requires its matching scenario. |
| Sight | Restrict the human map to the community's visible neighborhood. |
| Restart / R | Recreate the exact same seeded episode. |
| New seed | Increase the seed by one and create a new world. |
| WASD | Move in manual mode. |
| 1, 2, 3 | Gather food, wood, stone in manual mode. |
| 4, 5, 6, 7 | Experiment with Fire, Cooking, Basic Tools, Storage in manual mode. |
| C | Conserve in manual mode. |
| Esc | Exit. |

The window scales to fit its size. For readable text, use roughly 1152x720 or larger. Automatic turns occur every 0.8 seconds at 1x, while animation draws at up to 60 frames per second. Resizing and pausing do not advance the simulation.

## How it connects to the code

`src/alive/viewer.py` creates an `Episode`, feeds its observation to the selected agent, and calls the same `Episode.step()` used by training and evaluation. It renders the new world state and interpolates the last movement. Manual control replaces only action selection. Particle effects and terrain decoration consume no environment RNG.

`tests/test_viewer.py` runs with SDL's off-screen driver. It checks that the viewer reproduces the rule-agent simulation, stops at completion, respects pause/reset, handles manual actions, and renders both sight modes. Tests skip cleanly when Pygame is not installed.

## Interpreting results

1. Start with Rules, read the goal banner, and press Play or Step.
2. Pause and open Results. Population retained is relative to the initial population; shortage turns count turns with any missing food. Discovery counts are not a win score.
3. Click the chart or timeline, or use Previous/Next, to inspect a recorded turn. The selected population, inventories, action, and ledger belong to that turn. The simulation and policy memory stay at the live position; Play or Step resumes there, not in the past.
4. Read the resource ledger: F/W/S means food/wood/stone. Net inventory changes reconcile gathering against research, upkeep, eating, travel, and passive decay. Shortage is unmet demand, not an additional inventory deduction. Values displayed on screen are rounded; exported values retain precision.
5. Compare baselines runs independent Random and Rules episodes on the identical scenario and seed. They run to completion; a partial live run is not directly comparable to their final outcomes. A single seed cannot establish which controller is generally better. Use the existing multi-seed evaluation for that.
6. Export JSON / CSV saves the **entire current recording**, regardless of the selected inspection turn, under `results/viewer_runs/`. JSON includes initial and subsequent world states, scenario settings, turn facts, cumulative summary, and any reference runs. CSV provides one row per turn for spreadsheet analysis. Restarting or changing scenario/controller/seed clears the recording, so export first if needed.

Green technology labels mean currently active, not merely discovered. Population loss is irreversible within Level 1; there is currently no population growth or reproduction. Reaching 256 turns is completion, not automatically a successful survival outcome. The displayed reward is the existing RL training signal and should not be treated as a separate game score. The viewer does not infer why an agent chose an action.

The rule agent is a baseline, not trained AI. It can still make poor decisions under current settings. Population loss on screen reflects real shortages. There is no hidden visual mode that makes the community healthier. A trained checkpoint can be loaded with `--controller rl --checkpoint PATH`; the short smoke model is not expected to behave well.

To inspect a still image without opening a persistent window, use `--preview results/viewer/preview.png`. This executes eight baseline actions, draws the resulting frame, saves the PNG, and exits. In manual mode it saves the initial state.
