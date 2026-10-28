# ALIVE: Project handbook

Adaptive Life in Virtual Environments

Version 0.10 · Reviewed 2026-10-28

> Maintained snapshot. Implemented features, proposals, and open questions are distinct.


## Start here

A living handbook for a world where communities learn, develop technology, and exchange knowledge. Start with the vision. Then check what actually exists.


### The idea

ALIVE is an extensible simulation sandbox for exploring how abstract communities adapt through technology and knowledge exchange under resource pressure. Reinforcement learning is the intended decision-making direction; the engine defines what is possible, and communities learn which choices work.

- Current prototype: 1 community
- Technology graph: 4 nodes
- Latest verified tests: 24 passed
- Main missing behavior: Knowledge exchange


### What a newcomer should understand

- Today an agent represents an entire community, not an individual person or a real culture. Individual-level agents are a documented future option, not implemented.
- Survival creates pressure. Technological development and social interaction are the distinctive goal.
- The current prototype proves parts of the engine, not the complete cultural-diffusion idea.
- The default viewer uses a hand-written rule policy. Running the viewer does not itself train an agent.
- Multiple communities, sharing, and scheduled researcher-controlled world changes are not implemented yet.


### Current priority: make technology reliably worthwhile

A paired stable-scenario ablation now compares the same rule strategy with research enabled and disabled. Research wins 11/20 seeds but is slightly worse on average, with greater variance: current technology choices are context-dependent and their costs are not reliably recovered within 256 turns. Next isolate which node/scenario creates value before asking RL to learn the choice. The broader multi-community demonstration still needs team agreement.


### Choose your reading route

| Reader | Where to go | What you will learn |
| --- | --- | --- |
| Advisor / first-time visitor | Vision → Current state → Roadmap | Purpose, honest progress, and proposed next milestone |
| Developer | How it works → Work queue → Decisions | Architecture, next tasks, and unresolved contracts |
| Researcher | Research → Current state → Journal | Questions, evidence standards, and what has actually been tested |
| Team member | Work queue → Journal → Team & upkeep | What needs attention and how to keep this handbook current |


### How to read status labels

- Implemented: code exists. This does not prove good behavior.
- Verified: a specified check passed, with evidence and date.
- Proposed: a recommendation, not an approved commitment.
- Open: an unresolved choice or unassigned task.
- Deferred: intentionally outside the immediate milestone.


### A maintained snapshot, not automatic project monitoring

This handbook was reconciled against the local code, documentation, and recent discussion on 2026-10-10. It does not automatically inspect GitHub or update after code changes. Owners, deadlines, learning-quality claims, and advisor approvals must be recorded explicitly rather than inferred.


## Vision & goals

Build a small complete system that can grow—not a huge technology list with little meaningful behavior.


### The problem we want to explore

Technology development does not happen in isolation. Communities have limited resources and must choose between immediate needs, experimentation, adoption, and sharing. ALIVE makes those choices observable within a controlled artificial world. It is a development platform with focused experiments, not a predictor of real societies.


### Central question

How do environmental pressure, technological prerequisites, and knowledge exchange shape the development and survival of virtual communities? A later focused experiment asks when sharing helps the sharing community, and when it benefits a competitor instead.


### Intended experience

- Communities learn action strategies through RL rather than following a prescribed technology path.
- Technology nodes define capabilities with prerequisites, resource costs, maintenance, and context-dependent effects.
- Different conditions make different strategies useful; technology is not automatically beneficial.
- Communities eventually discover, adopt, retain, and share knowledge.
- Researchers control environmental scenarios and interventions. Agent terraforming is not the requested feature.
- Users can pause, inspect outcomes, compare experiments, and understand the assumptions behind the world.


### Scope boundaries

| Core direction | Not an immediate requirement |
| --- | --- |
| Cultural and technological adaptation | Biological mutation and reproduction systems |
| Small graph with meaningful trade-offs | Infinite traits or open-ended invention of executable capabilities |
| RL choices within a defined action space | Human-level intelligence or unrestricted actions |
| Controlled synthetic experiments | Predictions about historical or modern societies |
| Transparent community-level simulation | A simulation of every individual person |
| Explainable outcomes and recorded costs | Claims to know a policy's intentions |


### How the idea evolved

Earlier discussions explored biological traits, trait trees, and Spore-inspired presentation. The advisor's technology-sharing suggestion shifted the direction toward abstract communities and cultural diffusion. RL was subsequently requested as the central learning approach. Those older ideas remain background, not automatically active requirements.


### Game references

Spore remains a reference for visible progression and approachable simulation. On 2026-10-15 the user proposed Age of Empires II as the stronger interface/world reference: readable resource management, an inhabited map, recognizable production/research locations, and clear progression—without combat. ALIVE is not a clone of either game, and should use original art, terminology, proportions, and interaction design.


### Future direction: individuals within communities

The user requested assessing and documenting individual-level agents as a later extension. Communities could become groups containing independently acting individuals with their own needs and knowledge. This preserves the cultural-diffusion idea while changing its resolution. See Individual agents for feasibility, trade-offs, and a bounded pilot. It is not a switch in the current prototype.


### Project sources

- Technology-development concept: ALIVE_Technology_Development_Simulation_Concept.md
- Agent design (includes future features): ALIVE_Agent_Design.md
- Workbook planning baseline: ALIVE_Workbook_1_Content.md


## Current state

The foundation works. The distinctive multi-community behavior remains to be built and demonstrated.


### Capability inventory · reviewed 2026-10-10

| Capability | Status | Evidence / limitation |
| --- | --- | --- |
| Seeded grid, food / wood / stone | Implemented | Immutable models, world, and stable/scarcity presets |
| Move, gather, experiment, conserve | Verified | Legal masks and deterministic action resolution tested |
| Fire, Cooking, Basic Tools, Storage | Implemented | Prerequisites, progress, effects, upkeep, and active-state handling |
| Random and rule policies | Verified | Complete episodes and reproducibility checks |
| Recurrent PPO training + checkpoint playback | Implemented | Optional RL packages; infrastructure and gradients tested, learning quality not established |
| Animated local viewer | Verified | Same Episode engine as evaluation; default controller is rules |
| Results dashboard and history inspection | Verified | 15-test suite passed; inspection and references do not change live state |
| JSON / CSV recording export | Verified | Turn facts, resource ledger, states, settings, and optional reference runs |
| Multiple communities / knowledge sharing | Not implemented | Single community in current state and observation contracts |
| Scheduled environmental interventions | Not implemented | Scarcity is an initial preset, not an event that occurs mid-run |
| Large editable technology graph | Not implemented | Current definitions are in Python; observations and policy contracts also need extension |
| Evidence of useful learned specialization | Not demonstrated | Requires controlled training and held-out evaluation |


### Current prototype limitation

The repaired rule policy proves that the stable environment permits survival and advancement beyond Fire, but progress varies: 15/20 runs complete Cooking, 6/20 Basic Tools, and 2/20 Storage. Scarcity completes only Fire in 2/20 runs and ends near 6.77 people on average. This is a baseline improvement, not proof of strong balance, useful RL, technology specialization, or recovery.


### Measured baseline diagnosis · seeds 0–19 · 2026-10-10

| Scenario / controller | Mean final population (starts at 40) | Discovery / termination outcomes |
| --- | --- | --- |
| Stable / Rules | 12.85 | 0/20 runs completed a discovery; all reached 256 turns |
| Scarcity / Rules | 4.81 | 0/20 runs completed a discovery; all reached 256 turns |
| Stable / Random | 0.00 | 18/20 completed a discovery; all collapsed |
| Scarcity / Random | 0.00 | 7/20 completed a discovery; all collapsed |


### Rule-policy repair · paired seeds 0–19 · 2026-10-15

| Scenario | Before → after mean final population | Before → after discovery outcomes | Interpretation |
| --- | --- | --- | --- |
| Stable | 12.85 → 20.0676 | 0/20 → 20/20 runs; 43 nodes: Fire 20, Cooking 15, Basic Tools 6, Storage 2 | Stable foundation gate improved: survival and multi-branch progress now occur together |
| Scarcity | 4.81 → 6.7744 | 0/20 → 2/20 Fire; no later nodes | Population improved slightly, but scarcity remains an explicit limitation |


### Technology-value ablation · stable seeds 0–19 · 2026-10-16

| Condition | Mean final population | Mean shortage / return | Result |
| --- | --- | --- | --- |
| Research enabled | 20.0676 (50.17% retained; SD 24.55 points) | 39.8648 / 165.40 | Mean 2.15 completed nodes |
| Same rule policy; research disabled | 20.4332 (51.08% retained; SD 13.80 points) | 39.1335 / 195.33 | No experiment actions or discoveries |
| Enabled minus disabled | −0.3656 people (−0.91 percentage points) | +0.7313 shortage / −29.93 return | Enabled wins 11 seeds; disabled wins 9; result is mixed, not a technology benefit claim |


### Diagnosis: why the prototype falls short

- Rules gathers its target whenever the action is legal, without comparing yield against demand. A depleted deposit regenerates enough to keep gathering legal, trapping the policy in low-yield collection.
- On stable seed 42, Rules gathered food 240/256 turns, stayed in one position for the final 100 turns, and researched Fire only five times (60% discovery). First shortage was turn 35; final population was about 15.87.
- The seed-42 starting food deposit regenerates 0.7892 food/turn while the initial 40 people require 2 food/turn before other costs. This describes a local trap, not proof that the whole world cannot sustain them.
- Research only occurs at food reserves of at least 20; recurrent shortages prevent further attempts. Repair resource planning before assuming that lowering food demand is the answer.
- Population loss exists but population growth/recovery does not. A proficiency field exists but no mechanic improves it. Discovery and post-discovery improvement must not be conflated.
- Random can discover technology while dying. Discovery counts alone are not a sufficient success metric.
- This diagnostic batch is 80 deterministic episodes, not an RL evaluation or a balance fix. Neither rule-controller collapse nor useful RL behavior is established by these results.


### Diagnostic records

- Original aggregate measurements and seed-42 trace summary: docs/handbook/evidence/2026-10-10-baseline-diagnosis.json
- Paired rule-policy repair measurements and limitations: docs/handbook/evidence/2026-10-15-rule-baseline-repair.json
- Paired technology research ablation and per-seed deltas: docs/handbook/evidence/2026-10-16-technology-ablation.json


### Research strategy comparison · stable seeds 0–19 · 2026-10-28

Configurable none, fire, cooking (Fire then Cooking), and all research paths are implemented. A matched 20-seed comparison retains mean populations of 51.08%, 47.51%, 51.90%, and 50.17% respectively. Cooking is +0.82 percentage points versus no research, with higher variance; this does not establish superiority, isolated node causality, or RL learning. All 24 tests pass, including seven tests written before implementation. Evidence: docs/handbook/evidence/2026-10-28-research-strategies.json.


### Earlier verification · 2026-10-16

On 2026-10-16 the local suite passed 17 tests; two optional RL tests skipped because PyTorch/Gymnasium were not installed in the viewer environment. Tests cover the multi-technology seed-42 regression and verify that the ablation preserves paired seeds, writes configuration and every full trace, and performs no experiment action in the restricted condition. Existing reproducibility, hidden-information isolation, action legality, resource accounting, viewer equivalence, history, comparison, and export checks still pass. This verifies deterministic baseline/experiment behavior, not learned-policy quality.


### Claims we can and cannot make

| Defensible now | Not defensible yet |
| --- | --- |
| A repeatable community simulation runs and can be inspected | Communities have learned sophisticated strategies |
| Training and evaluation infrastructure exists | RL consistently outperforms baselines |
| Technology costs and effects are explicit | Different conditions create robust technological specialization |
| A one-community prototype is operational | Technology spreads among interacting communities |


### Evidence locations

- Implementation and setup: README.md
- Engine and training explanation: docs/LEVEL_1_GUIDE.md
- Viewer interpretation: docs/VIEWER_GUIDE.md
- Simulation tests: tests/test_level1.py
- Viewer tests: tests/test_viewer.py


## How it works

The world applies the rules. A policy chooses an action. Training changes the policy—not the rules of physics.


### One simulation turn

Scenario + seed → World state → Local observation + legal mask → Policy selects action → Resolver applies consequences → New state + reward + record


### What the agent is

Each agent is a community state plus a decision policy. The current community stores position, aggregate population and labor, inventory, technology progress, and previous action. Its observation contains 128 features with a radius-two neighborhood and a mask for 12 actions. Policy memory can carry recent information; the engine does not give the agent the complete observer map.


### Current technology graph

Two small prerequisite branches. Green active labels in the viewer mean upkeep requirements are currently satisfied; discovery alone does not guarantee continued benefit.

```text
Fire ────────> Cooking
Basic Tools ─> Storage
```


### Decision systems

| Controller | How it chooses | Does it learn here? |
| --- | --- | --- |
| Random | Samples legal actions | No |
| Rules | Uses a hand-written survival / research strategy | No |
| Manual | A person selects actions | No |
| RL playback | A saved recurrent neural policy chooses actions | Memory changes; weights do not |
| RL training | Rollouts produce rewards; PPO updates weights | Yes, across training episodes |


### Code map

| Area | Files | Responsibility |
| --- | --- | --- |
| State and mechanics | environment/models.py, world.py, resolver.py | Immutable state, deposits, transition costs and effects |
| Technology and actions | environment/technology.py, actions.py | Prerequisite graph, action encoding, legal masks |
| Learning interface | environment/observations.py, rewards.py, episode.py, rl_environment.py | Observations, rewards, reset/step, Gymnasium adapter |
| Policies and training | baseline_agents.py, rl_policy.py, train.py | Reference policies, GRU actor/critic, recurrent PPO |
| Analysis and presentation | evaluate.py, viewer.py, viewer_results.py | Held-out evaluation, animation, recording and exports |


### Practical boundaries

- The engine and its tests use the Python standard library. Python 3.11+ is required.
- Viewer dependencies are optional Pygame; it is a native desktop window, not this website.
- RL adds NumPy, PyTorch, and Gymnasium. No LLM is currently used.
- Adding technology nodes is not just a visual edit: observation dimensions, action catalogs, masks, checkpoints, and tests must remain compatible.
- The current reward emphasizes population retention and penalizes shortages and losses; it does not award a direct technology bonus.


### Hardware and cost

The supplied Ryzen 7 laptop with 16 GB RAM is suitable for the documentation site and small CPU simulation/viewer runs; no discrete GPU is required for these. Longer RL training must be benchmarked. The desktop RTX 3060 Ti and 32 GB RAM may support larger experiments, but speed, VRAM fit, and training cost are not yet measured. Measure steps/second, wall time, RAM, and held-out outcomes before promising a training schedule or buying compute.


## Interface vision

Proposed direction: an Age of Empires II-inspired resource-management view adapted for an AI-observation simulation with no combat.


### Why this direction fits

Age of Empires II communicates resources, population, map activity, selection, construction, and technological progression at a glance. Those are close to ALIVE's needs. The useful lesson is its information hierarchy and sense of a functioning settlement—not its warfare, factions, win conditions, art, or exact interface.


### Borrow, adapt, and avoid

| Borrow as a design principle | Adapt for ALIVE | Avoid |
| --- | --- | --- |
| Readable resource strip | Food, wood, stone, population, active controller, turn and speed | Copying AoE icons, typefaces, frames, colors, sounds or exact placement |
| Living workers and visible activity | Show symbolic work parties until individuals become real agents; label the abstraction | Pretending each rendered person has independent AI today |
| Town-centered settlement | A community hub anchors identity, stores and inspection; buildings only imply mechanics that actually exist | Decorative buildings that falsely claim production systems |
| Contextual selection panel | Inspect community, resource deposit or technology and show relevant facts/actions | A dense permanent panel containing every metric |
| Technology progression | A dedicated technology view with prerequisites, progress, cost, effect and upkeep | Combat units, military upgrades or a single mandatory age ladder |
| Minimap and fog of war | Later use for orientation and to distinguish observer knowledge from agent knowledge | Showing hidden information as if the policy can see it |
| Event notifications | Shortage, discovery, depletion and environmental-change alerts linked to the timeline | Constant noisy text or unexplained score popups |


### Proposed screen hierarchy

| Region | Primary purpose | First-version contents |
| --- | --- | --- |
| Top resource bar | Answer 'How is the community doing?' immediately | Food, wood, stone, population, turn, controller and simulation speed |
| Central world | Make gathering, travel and research visibly legible | Larger map, community hub, resource sites, work-party animation, selection highlight and fog toggle |
| Bottom context panel | Explain the selected object without leaving the world | Identity, current action, local yields, technology status and exact resource consequences |
| Simulation controls | Control observation rather than command an RTS army | Play/pause, step, speed, restart, scenario/seed and controller; manual actions only in Manual mode |
| Notification rail | Tell the run's story | Prioritized alerts that open the corresponding turn in history |
| Technology overlay | Make the graph a central strategic system | Prerequisite nodes, progress, costs, active effects and maintenance state |
| Results / replay view | Move from watching to understanding | Population/resources over time, discoveries, shortages, comparison and export |


### The user is an observer first

AoE is built around constant player commands. ALIVE's main mode observes an autonomous rules or RL controller. The interface must not imply that the human is choosing every action. In automatic modes, clicking inspects and explains; in Manual mode, the same context area can expose legal commands.


### Visual principles

- The world should occupy most of the screen; supporting data frames it rather than competing with it.
- Large numbers and icons carry current state; exact accounting appears on selection or in Results.
- Resources must look collectible, depleted and regenerating, and actions need visible start/result feedback.
- Technology should visibly change the settlement or workflow only when the corresponding mechanic is active.
- Color, animation and audio should communicate state consistently and remain readable without relying on color alone.
- Original artwork and naming should evoke a grounded settlement simulation without reproducing Age of Empires II's protected assets or trade dress.


### Step-by-step redesign gates

| Step | Reviewable output | Do not proceed until |
| --- | --- | --- |
| UI-1 · Experience brief | One-page statement of user role, first 10-second questions and visual references | The team agrees whether Watch is observer-first and what Manual mode means |
| UI-2 · Low-fidelity wireframe | Annotated desktop layout with information priority and interaction states | The layout is understandable without final art |
| UI-3 · World readability prototype | Map/hub/resources/work parties with selection and state feedback | A new viewer can identify activity and resource condition |
| UI-4 · Context and controls | Resource bar, selection panel, simulation controls and legal manual actions | Controls never imply unavailable mechanics |
| UI-5 · Technology and events | Graph overlay, research feedback, alerts and history links | Discovery cost, progress, effect and upkeep are understandable |
| UI-6 · Results integration | Replay/comparison/export using the same visual language | A viewer can explain why a run succeeded or failed |
| UI-7 · Polish and accessibility | Original visual assets, motion/audio settings, scaling and keyboard support | Functional and behavioral validation still passes |


### Relationship to current development

This is a proposed presentation direction, not authorization to redesign the simulation engine or add buildings, jobs, markets or production chains. The foundation-first baseline repair remains the next engineering priority. UI-1 and UI-2 can be planned alongside it; implementation should follow approved wireframes and truthful mechanics.


## UI rebuild plan

An execution contract for replacing the current viewer with an original, Age of Empires II-inspired non-combat presentation while preserving ALIVE's simulation rules and observer-first purpose.


### Definition of success

A first-time viewer can tell what the community is doing, which resources are healthy or threatened, what technology is being pursued, why population changes, and whether the controller is Rules, Manual, or RL—without reading a console or mistaking decorative activity for implemented mechanics. The redesign borrows information hierarchy and inhabited-world principles, not Age of Empires II assets, exact layout, terminology, or trade dress.


### Locked scope for the rebuild

| Included | Explicitly excluded | Reason |
| --- | --- | --- |
| A new 2D viewer shell, world presentation, controls, technology view, alerts, replay/results integration, original visual assets, and accessibility/performance options | Changing food demand, regeneration, rewards, actions, technology effects, population rules, or controller logic | Presentation and engine behavior must be reviewed independently |
| Observer-first Watch mode plus an explicitly labeled Manual mode | Turning automatic modes into an RTS command interface | Rules and RL agents remain the decision makers during autonomous runs |
| A community hub and symbolic work parties | Claiming rendered people are independent agents or that decorative buildings run production chains | The current agent is one aggregate community |
| Truthful displays of implemented data | Invented scores, ages, buildings, markets, jobs, or combat | The interface must not outrun the simulation |
| Desktop/laptop scaling and CPU-friendly effects | A 3D rewrite or GPU requirement | The milestone is a readable 2D simulation; the renderer choice is resolved at Phase 0 |


### Renderer/platform decision

| Option | Strength for ALIVE | Cost or weakness | Verdict |
| --- | --- | --- | --- |
| Pygame-ce | Same Python process as Episode/RL; current tests and recording code transfer directly; smallest migration and easiest deterministic parity | No visual scene editor, modest layout/animation tooling, and more custom UI/asset-pipeline code | Recommended for the next production milestone if the spike meets readability and frame-time targets |
| Arcade | Python-native with OpenGL rendering, Camera2D, tile-map support, scene/sprite organization, and a widget/layout system | Requires a renderer rewrite and OpenGL 3.3+ while still leaving most presentation architecture in Python; limited payoff over a well-structured Pygame V2 | Useful fallback if Pygame performance is measured as the blocker; not the default migration |
| Godot 4 | Best visual authoring: dedicated 2D renderer, scenes, TileMap, animation, particles, shaders, UI controls/containers, responsive scaling, audio, and packaging | Python is not an officially supported gameplay language; ALIVE would need a GDScript/C# client plus a versioned IPC/replay protocol to the Python engine, creating two runtimes and more debugging | Best long-term presentation client if polished public distribution becomes the priority; premature for the next core proof |
| Phaser / browser client | Easy link-based sharing and WebGL/Canvas browser delivery | JavaScript/TypeScript frontend plus a server, WebSocket, or exported-replay boundary; browser deployment and security add scope | Consider only when remote browser access becomes an approved requirement |


### Approved platform direction

Keep the Python simulation/RL engine and current Pygame-ce viewer while the team proves the core survival, technology, and learning goals. Do not spend the next milestone on a renderer bake-off or visual rewrite. When the behavioral milestone succeeds, reopen this plan: Pygame V2 remains the lowest-risk upgrade, while Godot remains the stronger option if polished public presentation then justifies a second client/runtime.


### Proposed Pygame V2 file boundary

| Area | Proposed location | Single responsibility |
| --- | --- | --- |
| Application shell | src/alive/viewer_v2/app.py | Own the Pygame loop, route screens, and coordinate input; never implement simulation rules |
| Simulation session adapter | src/alive/viewer_v2/session.py | The only presentation module allowed to reset or advance Episode; expose immutable snapshots and recordings |
| Presentation models | src/alive/viewer_v2/view_models.py | Translate engine state into labels, percentages, alerts, and selectable objects without policy decisions |
| Layout and theme | src/alive/viewer_v2/layout.py; theme.py | Scale a 1600x900 reference layout to smaller windows and centralize colors, spacing, type, and motion settings |
| World and camera | src/alive/viewer_v2/world_renderer.py; camera.py; selection.py | Draw the terrain, hub, deposits, symbolic work parties, effects, camera transforms, and selection state |
| Screens | src/alive/viewer_v2/screens/ | Separate Watch, Technology, Results, and Guide views |
| Reusable interface | src/alive/viewer_v2/widgets/ | Resource bar, context panel, controls, notification rail, timeline, tooltips, and dialogs |
| Original assets | assets/viewer_v2/ | Project-owned icons, tiles, sprites, sound, and documented licenses/source |
| Verification | tests/test_viewer_v2.py; tests/viewer_v2/ | Behavioral parity, input/state safety, layout checks, and reviewed screenshots |


### Safe migration rule

Do not rewrite src/alive/viewer.py in place. Launch V2 separately with python -m alive.viewer_v2 while the current viewer remains the fallback. Episode and environment modules stay unchanged during the UI rebuild unless a separately documented engine gap is approved. Switch the normal launcher only after the final cutover gate; archive rather than immediately delete V1.


### Execution phases and hard gates · deferred until behavioral proof

| Phase | Concrete output | Acceptance gate before continuing |
| --- | --- | --- |
| 0 · Reopen and freeze the viewer baseline | After the core milestone succeeds, record current screenshots, controls, supported resolutions, tests, representative episode traces and frame time; confirm whether Pygame still meets the approved presentation goal | A new visual-work decision is recorded; renderer investigation occurs only if a measured requirement warrants it |
| 1 · Experience contract | One-page brief defining audience, observer/manual roles, first-10-second questions, navigation, interaction verbs, visual principles, and non-goals | User approves the brief; disputed terms and features are resolved in writing |
| 2 · Wireframe contract | Annotated 1600x900 low-fidelity screens for new run, active gathering, selected community/deposit, research, shortage, paused/manual, completion, and results | User can explain each state without narration; every visible control maps to a real mechanic |
| 3 · Architecture scaffold | V2 client, versioned session/data adapter, immutable view models, theme/layout system, placeholder screens, and automated smoke tests | Paused drawing and navigation never advance state; V1 and V2 produce identical engine traces for matched runs |
| 4 · Readable living world | Camera, map, community hub, deposit condition, symbolic work-party movement, action feedback, selection, and optional fog/observer cues | A new viewer identifies current activity, target resource, deposit health, and abstraction level in a short walkthrough |
| 5 · HUD and controls | Top resource/status bar, contextual bottom panel, play/pause/step/speed/restart, scenario/seed/controller setup, tooltips, and legal Manual actions | Mode is unmistakable; disabled controls explain why; clicks, resize, and keyboard input never cause accidental turns |
| 6 · Technology and event story | Technology graph overlay, progress/cost/effect/upkeep states, research feedback, prioritized notifications, and history links | The display matches engine records and distinguishes discovered from currently active technology |
| 7 · Results and replay | Integrate population/resource timelines, shortages, discoveries, comparison, inspection, and JSON/CSV export using the new visual language | Historical inspection cannot mutate/rewind the live episode; existing exports and same-seed comparisons remain equivalent |
| 8 · Original art, accessibility, and performance | Original production assets, readable icons/text, non-color status cues, motion/audio controls, quality fallback, and laptop profiling | All functional tests pass; reviewed 1600x900 and 1366x768 captures have no clipped critical controls; baseline laptop reaches at least 30 FPS with 60 FPS as the target |
| 9 · Cutover and documentation | Approved launcher switch, updated viewer guide/handbook, before-and-after evidence, and retained fallback path | User signs off on the complete run; regression suite and release checklist pass; no unapproved engine change is bundled |


### State set required before artwork

| State | What must be obvious | Required truth source |
| --- | --- | --- |
| Fresh run / paused | Scenario, seed, controller, goal of the run, and how to start | Session configuration |
| Gathering / travel | Who is represented, target, action, travel/activity feedback, expected and actual resource change | Recorded action and resource ledger |
| Deposit selected | Resource type, remaining amount, regeneration/depletion status, local accessibility | World/deposit snapshot |
| Community selected | Population, stores, current action, shortages, technology focus, and abstraction label | Community snapshot and turn record |
| Research | Technology, prerequisites, cost, progress, expected effect, and upkeep | Technology definitions and progress state |
| Shortage / decline | Which requirement failed, immediate accounting consequence, and relevant event turn | Resolver facts and population ledger |
| Manual mode | Legal actions, unavailable-action reason, and clear separation from autonomous control | Action mask and selected controller |
| Completion / collapse | Why the episode ended, outcome summary, and route to Results/replay | Episode termination and recording |


### Non-negotiable verification matrix

- Matched seed, scenario, maximum turns, and controller yield the same engine state/action trace in V1, V2, and headless Episode playback; animation timing may differ but decisions may not.
- Rendering, hovering, selecting, resizing, opening overlays, and inspecting history never call Episode.step. One deliberate step produces exactly one turn.
- Automatic modes expose inspection only. Manual actions use the engine's legal mask; rejected actions do not advance the turn or consume resources.
- The observer view labels information the policy cannot see. Fog or local-observation displays never imply the agent received the full map.
- Resource totals, discoveries, shortages, termination reasons, comparison runs, and exported records reconcile with the existing recorder.
- Each required state receives a reviewed screenshot at 1600x900 and 1366x768; critical information is not encoded by color alone.
- Profile startup, average and worst-frame timing, RAM, and any reduced-effects mode on the Ryzen 7 / integrated-graphics laptop before claiming performance.


### Estimated effort after approval

| Work | Planning range | Main uncertainty |
| --- | --- | --- |
| Experience brief + wireframes | 1–3 focused days | How quickly interaction and information decisions are approved |
| Scaffold + parity harness | 2–4 focused days | How tightly the current viewer is coupled to Episode and results helpers |
| World + HUD + controls | 4–8 focused days | Animation/art ambition and responsive-layout edge cases |
| Technology + events + results | 3–6 focused days | Reuse of existing results code and desired replay depth |
| Art/accessibility/performance/cutover | 3–7 focused days | Asset production and laptop profiling findings |
| Total first production version | 13–28 focused developer days | A planning range, not a deadline; engine changes or new mechanics are outside it |


### Change-control rules that reduce rework

- Approve and freeze the experience contract before drawing the final layout; approve the wireframe before production code or artwork.
- At each gate record deliverable, reviewer, decision, evidence, unresolved issue, and date in the journal. Approval freezes that phase's contract.
- Ideas discovered mid-phase go to a visible backlog unless they fix a blocker, correctness defect, accessibility failure, or accepted requirement.
- If implementation exposes a missing engine capability, stop at the adapter boundary and create a separate mechanic proposal; do not hide the change in viewer code.
- Use structural UI tests and reviewed reference screenshots. Avoid fragile whole-screen pixel equality for animation.
- A phase is not Done because it looks polished: its acceptance checks, regression tests, and documentation must also pass.
- Small revisions after real usability testing are expected. The goal is to eliminate ambiguous scope and avoid wholesale redesign, not to pretend feedback can be predicted perfectly.


### Renderer sources · official documentation checked 2026-10-15


#### [pygame-ce documentation](https://pyga.me/docs/)

pygame-ce project

Current API surface reviewed

Documents surfaces, events, sprites, input, audio, transforms, display scaling, and timing. These primitives are sufficient but require ALIVE to supply its own higher-level scene and UI architecture.


#### [Arcade installation and requirements](https://api.arcade.academy/en/stable/get_started/install.html)

Python Arcade

Stable requirements reviewed

Arcade remains Python-native but requires OpenGL 3.3+ or supported GLES. Camera, tile-map, and GUI documentation support its middle-ground assessment.


#### [Godot 2D introduction](https://docs.godotengine.org/en/stable/tutorials/2d/introduction_to_2d.html)

Godot Engine

Stable 2D feature overview reviewed

Documents Godot's dedicated 2D renderer, TileMap, animation, lighting, particles, and shaders.


#### [Godot scripting languages](https://docs.godotengine.org/en/stable/getting_started/step_by_step/scripting_languages.html)

Godot Engine

Stable language support reviewed

Official languages are GDScript, C#, C, and C++; Python is not an official gameplay language, so keeping the ALIVE engine in Python requires an explicit boundary.


#### [Godot multiple resolutions](https://docs.godotengine.org/en/stable/tutorials/rendering/multiple_resolutions.html)

Godot Engine

Stable scaling guidance reviewed

Documents base resolutions, stretch behavior, anchors, and UI scaling relevant to the proposed desktop/laptop interface.


#### [Phaser documentation](https://docs.phaser.io/)

Phaser Studio

Current framework overview reviewed

Phaser targets browser games with WebGL/Canvas using JavaScript or TypeScript; that improves sharing but adds a second-language/frontend boundary for ALIVE.


### Immediate project priority

Viewer V2 remains deferred and the existing Pygame viewer remains the observation tool. The first T03 net ablation is complete and found mixed value rather than a reliable technology benefit. Next run a node-level or scenario-controlled experiment to determine which technology effects repay their discovery/maintenance costs and under what resource conditions. Do not tune rewards or claim RL success yet.


## Roadmap

These are proposed engineering gates, not a new advisor-approved schedule. No new deadlines or task owners have been assigned.


### Milestones and exit criteria

| Milestone | Status | Deliverable / completion gate |
| --- | --- | --- |
| M0 · Foundation | Implemented | Repeatable single-community engine, policies, viewer, logs; functional tests pass |
| M0a · Repair and validate the baseline | Stable gate verified; scarcity limited | Yield/travel-aware gathering and resumable research are implemented. Stable seeds 0–19 improve survival and all complete technology; scarcity improves survival and 2/20 complete Fire only. |
| M1 · Freeze the next demonstration | Proposed | Team records the minimum community count, technologies, learning requirement, metrics, and acceptance threshold |
| M2 · Make technology matter | In progress · mixed net ablation | First research-enabled/restricted comparison found no mean population benefit. Isolate node/scenario value and define an evidence-backed trade-off before completion. |
| M3 · Demonstrate useful learning | Proposed | Train repeated seeds, evaluate held-out worlds against random/rules, report variance and costs; agree quantitative target before tuning |
| M4 · Two-community exchange | Proposed | Extend state, observations, policies, and logging; implement one bounded knowledge-transfer mechanic with tests and a complete demo |
| M5 · Researcher-controlled changes | Proposed | Scheduled abundance/scarcity or resource-change events can be replayed from configuration; compare recovery outcomes |
| M6 · Expand the sandbox | Deferred | Add larger graphs, more communities, editors, and richer visuals only after previous gates work |
| F1 · Individual-agent pilot | Deferred option | After core validation and multi-entity contracts: test 5–10 individuals with separate state/memory, shared policy, and one teaching mechanic. Independent of large-tree expansion; requires explicit team approval. |


### Recommended next demonstration

Two communities, a small technology graph, limited resources, and one opportunity to exchange knowledge. First prove that technology creates useful choices and the learning setup works; then integrate exchange. The workbook's older three-community / 8–12 technology criteria remain an unresolved planning difference, not a requirement silently removed here.


### What we should postpone

- A very large technology tree before existing technologies create meaningful choices.
- Advanced graphics that obscure whether the behavior is actually working.
- LLM integration before we can name a useful, measurable role for it.
- Real-world forecasting, complex diplomacy, reproduction, and warfare.
- GPU optimization before profiling the small system.


### Time expectations

No delivery dates or labor estimates are committed in this handbook. The existing workbook contains a provisional semester schedule; it needs reconciliation with code already completed and the RL-first direction. Break each approved gate into reviewable tasks, estimate them with the assigned developer, and budget an explicit validation period. Multi-agent training and reward design can take more iteration than adding a UI feature.


## Work queue

Start at the top. The immediate work is scope and behavioral validation—not another visual expansion.


### Proposed next actions


#### T01 · Agree on the next core demonstration

P0 · Open · Owner: Unassigned · team decision

Next action: Review M1 and resolve two communities vs workbook criteria. Record approval in D03 before treating it as committed scope.

Done when: Written scope, success criteria, and named reviewer.


#### T02 · Measure the current survival / research balance

P0 · Done · Owner: Implemented in current local workspace

Next action: Use the evaluation runner's configuration, full per-seed traces, CSV, summary, and fixed replay outputs for subsequent experiments.

Done when: Reproducible before/after evidence explains the original failure and repair; no engine balance change was disguised as a UI or policy fix.


#### T03 · Design a minimal meaningful technology trade-off

P1 · In progress · net ablation measured · Owner: Unassigned · experiment design review

Next action: The 2026-10-28 research-path comparison is complete; Cooking has a small sample mean advantage. Next isolate mechanisms or confirm on disjoint seeds before changing costs/effects. T03 remains open for causal validation.

Done when: Tests plus measurements identify a repeatable outcome difference attributable to a technology mechanic, not a hidden bonus or research-policy side effect.


#### T04 · Establish a learning-quality baseline

P1 · Open · Owner: Unassigned

Next action: Benchmark a short CPU training run, then plan repeated training seeds and held-out evaluation. Freeze metrics before tuning.

Done when: Training/evaluation evidence with variance, compute time, and an honest success or failure conclusion.


#### T05 · Specify the multi-community engine contract

P1 · Open · Owner: Unassigned

Next action: Define IDs, action scheduling, observations, shared deposits, rewards, episode termination, and checkpoint migration.

Done when: Reviewed design and test plan before expanding the single-community state.


#### T06 · Define one knowledge-transfer action

P2 · Open · Owner: Unassigned

Next action: Specify eligibility, distance, costs, adoption requirements, provenance, and how donor/recipient outcomes are measured.

Done when: A bounded sharing mechanic tied to the approved demonstration, with no assumed benefits.


#### T07 · Plan scheduled world interventions

P2 · Open · Owner: Unassigned

Next action: Choose a researcher-controlled event and specify timing, deterministic replay, and recovery metrics.

Done when: An approved event contract; agent environment modification remains out of scope.


#### T08 · Reconcile and maintain project documents

P1 · Open · Owner: Unassigned · documentation coordinator needed

Next action: Review handbook against the workbook, record approved differences, nominate an owner, and add one journal entry after each completed change.

Done when: One agreed source of truth with links to evidence and no conflicting active requirements.


#### T09 · Repair the rule baseline before expansion

P0 · Done · stable gate verified · Owner: Implemented in current local workspace

Next action: Use this deterministic reference in T03. Treat scarcity's zero-discovery result as an explicit limitation; do not silently tune environment balance inside the baseline task.

Done when: Regression rejects the depleted-food trap; paired seeds show stable survival/discovery improvement and record scarcity limitations without changing engine balance.


#### T10 · Review the individual-agent pilot

P2 · Deferred · Owner: Unassigned · future design review

Next action: Once baseline and multi-entity contracts are validated, review F1 and D10. Decide whether the extra resolution serves the technology-sharing question before implementation.

Done when: Explicit go/no-go decision, bounded pilot scope, ownership/reward rules, and a hardware benchmark plan; not an immediate implementation commitment.


#### T11 · Reopen the viewer V2 experience and wireframe contracts

P2 · Deferred until behavioral milestone · Owner: Unassigned · future user/design review

Next action: After the core survival/technology/learning acceptance criteria pass, review D14, confirm Pygame V2 versus a justified Godot client, and begin UI Phase 0. Do not start visual production work first.

Done when: Reopened decision with current evidence, approved experience brief, and annotated multi-state wireframe; every control maps to an implemented mechanic and deferred ideas are recorded.


### Task rules

Each task needs one owner, dependencies, a next action, a reviewer, and completion evidence. Open tasks above have no imposed due dates. Move work to In progress only when an owner starts it; mark it Done only after the acceptance check. Browser filters are views, not collaborative task editing or saved status changes.


## Development journal

A dated record where evidence exists. Undated implementation history is labeled rather than assigned invented dates.


### Project history


#### 2026-09-09 · Developing the advisor's project idea

Status: Recorded meeting

The team explored the intended purpose and technical direction, with scope still requiring refinement.

Evidence: meetings/2026-09-09-team.md

Next: The meeting planned a clearer direction for advisor discussion.


#### 2026-09-16 · Advisor discussion confirmed the broad direction

Status: Recorded meeting

Meeting notes record that the team was proceeding on the right track and identify hardware constraints. They do not approve the later two-community milestone or establish that RL quality was demonstrated.

Evidence: meetings/2026-09-16-advisor.md

Next: The recorded action was to establish an early codebase.


#### 2026-09-25 · Team organized initial development and assignments

Status: Recorded meeting

Tasks were divided for meeting records, workbook coordination, and an early testable build. Those historical assignments do not automatically assign today's work queue.

Evidence: meetings/2026-09-25-team.md

Next: Review the initial build and resolve remaining gaps.


#### Undated · earlier implementation · Single-community foundation and RL infrastructure

Status: Implemented

Built state models, actions, technology prerequisites, world generation, resolution, observation/reward contracts, baseline episodes, recurrent PPO, and evaluation. Exact implementation dates are not established by this journal.

Evidence: src/alive/; docs/LEVEL_1_GUIDE.md

Next: Separate infrastructure correctness from learned-behavior validation.


#### Undated · earlier implementation · Game-style local viewer

Status: Implemented

Added code-drawn isometric terrain, symbolic settlers, movement interpolation, gathering/research effects, manual controls, and CPU-friendly playback without changing the engine.

Evidence: src/alive/viewer.py; docs/VIEWER_GUIDE.md

Next: Make observed activity interpretable rather than merely attractive.


#### 2026-10-10 · Results and onboarding dashboard

Status: Verified

Added Watch / Results / Guide, population and shortage history, recorded-turn inspection, resource ledger, independent same-seed baselines, and JSON/CSV exports. The 15-test local suite passed; screenshots were inspected. No simulation balance changes or GitHub push.

Evidence: src/alive/viewer_results.py; tests/test_viewer.py

Next: Use results to diagnose whether technology produces worthwhile choices.


#### 2026-10-10 · Refocus on the distinctive project behavior

Status: Proposed

Discussion identified a gap between the current food-management prototype and the envisioned learning, technology development, and knowledge exchange. A two-community demonstration was recommended, not approved or implemented.

Evidence: Project discussion; decision D03

Next: Team review of scope and completion criteria.


#### 2026-10-10 · Central project handbook established

Status: Documentation

Consolidated vision, implementation inventory, architecture, proposed gates, work queue, decisions, reading register, and upkeep instructions into a local website and generated shareable handbook. Content validation and 33 installed-browser checks passed for edition 0.1, covering navigation, search, filters, print-content generation, mobile overflow, and the standalone edition. This entry records documentation work only.

Evidence: docs/handbook/; docs/PROJECT_HANDBOOK.md; docs/handbook/check-browser.mjs

Next: Assign a handbook owner, review planning conflicts, and approve publication separately.


#### 2026-10-10 · Rule baseline loses population and stalls research

Status: Measured diagnosis

A read-only diagnostic ran seeds 0–19 for Rules/Random in both presets. Rules completed no discoveries across 40 runs and retained mean populations 12.85 (stable) and 4.81 (scarcity). Random collapsed in all 40 runs but sometimes discovered technology. The rule agent's legal-action-only gathering choice traps it at low-yield regenerating deposits; a fixed reserve threshold stalls research. No code or balance was changed.

Evidence: docs/handbook/evidence/2026-10-10-baseline-diagnosis.json; src/alive/baseline_agents.py

Next: T09: repair and validate the baseline; T02: preserve before/after evidence.


#### 2026-10-10 · Validate the foundation before adding complexity

Status: User-supported priority

The user supports using a functioning baseline to establish that the environment and actions are solid before expanding. This is a development priority, not approval of a particular balance patch or evidence that the problem is fixed.

Evidence: Project discussion; decision D09; milestone M0a

Next: Specify the smallest measurable baseline repair and its checks.


#### 2026-10-10 · Individual agents requested as a later extension

Status: Future option documented

The user wants to explore individuals instead of one policy per community later. Feasibility review identifies shared-policy multi-agent RL as an option, with separate per-person state, knowledge, memory, rewards, and contention handling. The website now documents benefits, risks, migration work, and a proposed 5–10-person pilot. Nothing was implemented in the simulation.

Evidence: Individual agents section; decision D10; official PettingZoo and RLlib documentation

Next: Keep the current baseline priority; revisit F1 only after core validation and team approval.


#### 2026-10-15 · Age of Empires II-inspired non-combat interface

Status: Proposed design direction

The user proposed modeling ALIVE's presentation around Age of Empires II's resource readability and inhabited-world feel while excluding combat. The proposal adapts a top resource bar, large world view, contextual inspection, settlement anchor, technology overlay and event/replay systems for an observer-first AI simulation. It explicitly avoids copying assets or implying unimplemented individual or building mechanics.

Evidence: Interface vision section; decision D12

Next: Complete UI-1 experience brief, then review a low-fidelity wireframe before changing viewer code.


#### 2026-10-15 · Gated viewer V2 rebuild plan

Status: Execution plan drafted for review

The handbook now defines a side-by-side viewer_v2 architecture, locked presentation scope, nine implementation phases, required screen states, parity and state-safety checks, planning ranges, cutover criteria, and change-control rules. The plan keeps the existing viewer as a fallback and forbids unapproved simulation changes inside UI work. No viewer code or engine mechanics changed.

Evidence: UI rebuild plan section; task T11; decision D13

Next: Run Phase 0 and present the Phase 1 experience contract for approval before creating a production wireframe or code.


#### 2026-10-15 · Pygame now; keep a Godot migration path

Status: Platform recommendation documented

A renderer review concluded that Pygame-ce is the lowest-risk next client because it shares Python, Episode, tests, and recording infrastructure. Godot is the stronger long-term visual-authoring client but requires a second language/runtime and versioned communication boundary because Python is not officially supported for Godot gameplay scripting. Arcade and Phaser remain alternatives with narrower use cases. No renderer migration was implemented.

Evidence: UI rebuild plan renderer/platform decision; official renderer documentation; decision D14

Next: The user subsequently resolved the immediate direction: keep Pygame and defer visual expansion until the core behavioral goal succeeds.


#### 2026-10-15 · Behavior first; visual expansion later

Status: User-approved development priority

The user approved continuing with Pygame as the functional viewer and postponing the visual rebuild. Development now returns to proving the simulation's survival, technology, and learning loop. Viewer V2 and any Godot evaluation remain documented future work and should be reopened only after the behavioral milestone passes explicit acceptance checks.

Evidence: Project discussion; task T11; decisions D09 and D14

Next: Proceed with T09/T02: define the baseline-repair contract and preserve paired before/after evidence.


#### 2026-10-15 · Yield-aware rule baseline repairs the stable loop

Status: Implemented and measured

RuleAgent now uses only its observation plus remembered visited/seen cells to avoid low-yield deposits, navigate toward useful known resources, explore less repetitively, build reserves, and perform research in short resumable sessions around an emergency food floor. No environment, resolver, reward, action, observation, or technology definition changed. Across paired seeds 0–19, stable mean final population increased from 12.85 to 20.0676; every run completed Fire, 15 completed Cooking, 6 completed Basic Tools, and 2 completed Storage. Scarcity increased from 4.81 to 6.7744 and only 2 runs completed Fire.

Evidence: src/alive/baseline_agents.py; tests/test_level1.py; docs/handbook/evidence/2026-10-15-rule-baseline-repair.json; 16 tests passed

Next: T03: define a controlled technology-available versus restricted experiment; retain scarcity as an unresolved limitation.


#### 2026-10-16 · Technology research has mixed net value

Status: Implemented and measured

Evaluation now supports a paired technology ablation with the same RuleAgent and seeds, suppressing only experiment choices in the restricted condition. It saves configuration, every full trace, CSV/JSON summaries, replays, an HTML report, and paired deltas. Across stable seeds 0–19, research-enabled final population averaged 20.0676 versus 20.4332 without research; enabled won 11 seeds and lost 9, with greater variance, slightly more shortage, and lower mean return. Technology is therefore context-dependent under the current policy rather than reliably beneficial.

Evidence: src/alive/evaluate.py; results/technology_value_stable/ (local, git-ignored); docs/handbook/evidence/2026-10-16-technology-ablation.json; 17 tests passed

Next: Continue T03 with a predeclared node-level or scenario-controlled ablation; do not tune away the negative/mixed result.


#### 2026-10-28 · Configurable research strategies delivered with TDD

Status: Implemented and measured

Added none, fire, cooking and all research strategies, single-strategy CLI selection and matched comparison mode. Seven new tests were observed failing before implementation; the full 24-test suite passes without skips. Stable seeds 0–19 produced 51.08%, 47.51%, 51.90%, and 50.17% mean retention. Default and legacy no-research complete seed-42 trace fingerprints are preserved. No engine or reward tuning. The template-based design spec records configuration, implementation, tests and limitations.

Evidence: tests/test_research_strategies.py; docs/handbook/evidence/2026-10-28-research-strategies.json; docs/Research_Strategy_Design_Spec.docx

Next: Review the contribution and confirm the small Cooking advantage on independent seeds before drawing a general conclusion.


### Entry template

- Date / author / change title / related task and decision IDs.
- What changed and why; scope explicitly excluded.
- Evidence: code paths, PR or commit if one exists, configuration and result locations.
- Verification command and measured result; limits or failures.
- Follow-up action, owner, and approval needed.


## Research & experiments

Keep literature, hypotheses, and our own results distinct. A source can motivate a mechanic without validating our implementation.


### Proposed experiment register

| ID / question | Design | Evidence needed / status |
| --- | --- | --- |
| E01 · Does technology change outcomes? | Paired stable seeds 0–19; identical yield-aware rule strategy with experiment choices enabled vs suppressed | Initial net ablation completed 2026-10-16: enabled wins 11/20 but mean final population is 0.3656 lower and variance higher. Node/scenario isolation remains open. |
| E02 · Does RL learn a useful strategy? | Repeated training seeds, disjoint held-out world seeds, rules/random references | Learning curves, outcome distributions, variance, compute cost, failure cases. Not demonstrated. |
| E03 · When does sharing help the donor? | After multi-community implementation: transfer allowed vs disabled with matched scenarios | Donor and recipient outcomes, provenance, transfer costs, diffusion timing. Deferred until mechanic exists. |
| E04 · Can communities recover from changes? | Scheduled researcher-controlled resource intervention vs no intervention | Recovery time, population, resources and strategy changes. Deferred until event system exists. |


### Experiment record checklist

- Question and hypothesis before running the experiment.
- Code revision, scenario/technology/resolver/reward configurations, action/observation contract, and checkpoint identity.
- Separate training and evaluation seeds; record repeated training seeds.
- Baseline definitions, run counts, and agreed acceptance criteria.
- Per-run results and aggregate distributions, not just the best screenshot.
- Hardware, dependency versions, wall time, memory, and limitations.
- Interpretation and alternative explanations; distinguish a failed hypothesis from a failed implementation.


### Verified starting references · review depth stated


#### [Multi-agent Reinforcement Learning in Sequential Social Dilemmas](https://arxiv.org/abs/1702.03037)

Leibo et al. · 2017

Metadata + abstract checked 2026-10-10; full review pending

Studies learned multi-agent policies under social dilemmas and environmental factors, including resource abundance. Relevant background for a future cooperation/competition experiment; not evidence that ALIVE currently reproduces those findings.


#### [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)

Schulman et al. · 2017

Metadata + abstract checked 2026-10-10; full review pending

Introduces PPO policy-gradient methods. It is background for the chosen training approach, not a guarantee that ALIVE's recurrent implementation learns or matches published benchmark performance.


#### [PettingZoo Parallel API](https://pettingzoo.farama.org/api/parallel/)

Farama Foundation · official documentation

API overview and agent lifecycle reviewed 2026-10-10; not integrated

Documents simultaneous actions and dictionaries of per-agent observations, rewards, and termination flags, with active agents able to change. A reference for the future individual-agent contract, not a requirement to adopt a dependency now.


#### [RLlib Multi-Agent Environments](https://docs.ray.io/en/latest/rllib/multi-agent-envs.html)

Ray project · official documentation

Policy mapping and variable-sharing guidance reviewed 2026-10-10; not integrated

Documents mapping multiple agents to a policy and variable sharing. This supports the technical plausibility of a shared-policy design; it is not an ALIVE hardware benchmark or a guarantee of independent specialization.


### Literature backlog

The workbook includes cultural diffusion, network connectivity, social learning, and artificial-life references, as well as possible frameworks. Treat those as a reading register until titles, claims, methods, and applicability are reviewed. Do not copy version-specific software recommendations or numerical findings into project requirements without verification.


### Research note template

Record citation/link; review depth (metadata, abstract, or full paper); central claim and evidence; relevant assumption; possible ALIVE design implication; what does not transfer; reviewer/date; and any resulting decision ID. Keep exact quotations brief and attributable.


## Decisions & risks

A proposal is not a decision. Old documents remain useful evidence, but conflicts must be resolved rather than silently inherited.


### Decision register

| ID / topic | Status | Position and remaining action |
| --- | --- | --- |
| D01 · Current agent abstraction | Established direction | Today one agent is an abstract community. D10 records a future individual-level option without changing the current implementation. |
| D02 · Learning approach | User preference; team reconciliation open | Recent request makes RL central. Workbook lists RL as optional. Confirm the assessed deliverable with team/advisor. |
| D03 · Minimum next demo | Proposed | Two-community exchange recommendation vs workbook three-community / 8–12-node criteria. Approve or revise explicitly. |
| D04 · Environment changes | User clarification | Researchers alter conditions; agent terraforming is not the intended requirement. Timed interventions still need a design. |
| D05 · Large technology graph | Deferred expansion | User wants depth eventually. Prove small mechanics before expanding action/observation/checkpoint contracts. |
| D06 · Publication | Local-only for this delivery | Earlier instruction: do not push. No GitHub push or hosting deployment performed; sharing a hosted link needs a later publishing step. |
| D07 · Historical schedule / owners | Open | Workbook deadlines and contribution roles are provisional historical planning. Review before treating them as current assignments. |
| D08 · LLM role | Deferred | Possible later assistance is not part of the current engine or next proposed behavioral proof. |
| D09 · Foundation-first priority | Stable baseline implemented and measured | The rule policy now demonstrates survival plus technology in stable seeds without engine balance changes. Scarcity remains limited. Next prove technology causality with a paired experiment before RL expansion. |
| D10 · Individual-level agents | User-requested future option | Assess and preserve individuals within communities as a feasible future direction. Proposed small shared-policy pilot; no immediate scope switch, performance guarantee, or team/advisor approval. |
| D11 · Discussion capture | User request | Record meaningful ideas, concerns, findings, and decisions in the handbook after project discussions. This is a manual update workflow, not background monitoring or a verbatim archive of every chat. |
| D12 · Interface reference | User-proposed direction | Use Age of Empires II as a reference for information hierarchy, resource management and an inhabited non-combat world. Produce UI-1/UI-2 for review before viewer implementation; use original assets and do not imply mechanics that do not exist. |
| D13 · Viewer V2 execution | Deferred plan | The gated V2 plan is preserved but not active. Reopen it only after core behavioral acceptance criteria pass; preserve engine parity and retain V1 until any future cutover. |
| D14 · Renderer platform | User-approved direction | Keep the Python engine and Pygame-ce viewer for current development. Defer Godot evaluation and major visual work until survival, technology, and learning goals are demonstrated; then revisit the renderer using current evidence. |
| D15 · Technology net value | Measured finding; mechanism unresolved | The first stable 20-seed research ablation shows mixed, near-zero average population value and higher variance. Preserve the result. Isolate node/scenario effects before tuning mechanics or beginning serious RL training. |


### Risk register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Scope expands before a complete core loop | Large project with little demonstrable behavior | Gate expansion on M2/M3 evidence |
| Food pressure crowds out technology | Simulation fails to express intended experience | Measure failures before reviewing balance |
| Reward hacking / misleading research bonuses | Policy maximizes score without useful adaptation | Inspect component rewards and held-out outcome metrics |
| UI polish is mistaken for intelligence | Readers overestimate learning and emergence | Label controller and separate functional vs behavioral evidence |
| Checkpoint and feature contracts drift | Old models silently become incompatible | Version/configure contracts and reject incompatible models |
| One seed or one training run looks convincing | False confidence in general performance | Repeated training seeds, held-out worlds and variance |
| Documents diverge | Team works toward different deliverables | Update handbook, journal and decision register together |


### Decision template

Give each decision an ID, date, owner/approver, status, problem, alternatives, chosen option, consequences, evidence, and review trigger. If superseded, retain the old record with a link to the replacement; do not erase history.


## Individual agents

Technically feasible with a bounded multi-agent redesign. Each person could act and learn separately while communities remain the social structure around them.


### Feasibility verdict

Yes, this is a plausible extension—not a feature we can enable in the current viewer. Existing grid mechanics, resource/technology definitions, and policy-network ideas can be reused. The single-community state, resolver, observations, reward accounting, episode lifecycle, trainer rollouts, checkpoint contract, and viewer need substantial adaptation. This conclusion is an architectural inference supported by standard multi-agent interfaces, not a prototype benchmark.


### What would actually change?

| Aspect | Today | Proposed individual-level model |
| --- | --- | --- |
| Decision maker | One policy selects an action for a community | Each living individual chooses an action from its own observation |
| Population | An aggregate number can decline fractionally | Count living individuals; needs/health/death rules must be defined explicitly |
| Location and needs | One position and inventory | Per-person position, energy/hunger, inventory or access rights |
| Knowledge | One community technology-progress record | Personal knowledge; optional collective assets and an aggregate adoption view |
| Memory | One recurrent state for the community | Separate recurrent memory and trajectory for each individual |
| Community structure | The agent itself | Membership, shared infrastructure and institutions; not automatically a second controller |
| Interactions | No other decision-making entities | Resource contention, teaching, cooperation or exchange if those actions are implemented |


### What this could add to ALIVE

- Knowledge could be held by some people rather than instantly belonging to every member of a group.
- Teaching can create visible adoption chains and bottlenecks, with recorded teacher/recipient provenance.
- Division of labor or specialization could emerge if the incentives and available actions support it; it is not guaranteed by adding individuals.
- Knowledge may disappear when its last holder leaves or dies unless it is retained in others or a defined shared artifact.
- Community outcomes can be aggregated from personal outcomes, making cooperation costs and benefits more explicit.


### Many agents do not require many neural networks

A proposed efficient design shares one small RL policy's weights among individuals but supplies each with its own observation and recurrent memory. Training can use their separately recorded experience. Shared weights do not mean shared inventories, knowledge, memory, or identical actions. Different observations and stochastic choices can produce different behavior; persistent roles need appropriate state and incentives. RLlib documents many-to-one policy mapping, but adopting RLlib itself is optional.


### Proposed world tick

Snapshot local observations → Each live person chooses → Resolve conflicts under a documented rule → Apply transfers and individual costs once → Update lifecycle and record outcomes → Produce per-agent rewards / next observations


### Design choices to settle before implementation

| Choice | Why it matters | Pilot recommendation, not an approved rule |
| --- | --- | --- |
| Time and contention | Sequential order can advantage the first agent; simultaneous choices can target the same deposit | Simultaneous intent collection with reproducible conflict resolution; never allow double harvesting |
| Personal vs shared inventory | Undefined ownership causes duplicate resources or invisible subsidies | Start with explicit personal inventory and auditable transfers; defer complex communal stores |
| Knowledge ownership | A community label must not grant instant knowledge to all members | Personal progress and one bounded teaching action with costs, prerequisites, and provenance |
| Rewards | Purely selfish rewards can discourage helping; shared rewards can hide free-riding | Specify the question and evaluate personal and group outcomes before selecting reward weights |
| Deaths and terminal conditions | One person's death must not incorrectly end everyone else's rollout | Stable IDs, per-agent termination, memory reset, and an explicitly separate world-end condition |
| Growth and reproduction | Turns a finite pilot into a changing population and adds substantial complexity | No births in the first pilot; do not promise recovery or demographic realism |
| Knowledge vs policy learning | Trained policy weights are not the world's technology knowledge | Keep explicit personal knowledge separate from neural parameters and recurrent memory |


### Proposed pilot progression · F1

| Step | Bounded deliverable | Completion evidence |
| --- | --- | --- |
| 1 · Mechanical pilot | 5–10 individuals, one small map, survival/gathering, no births or complex society | Separate positions/actions; no negative or duplicated resources; reproducibility and fair conflict tests |
| 2 · Learning pilot | Shared policy with individual observation, masks, memory and trajectories | Held-out survival results vs rule/random references; no memory or observation leakage |
| 3 · Knowledge pilot | A tiny graph and one costly teaching action between eligible individuals | Knowledge-transfer logs; no automatic global unlock; recipient/donor outcomes measured |
| 4 · Community membership | Small groups and an aggregate community view, without an extra hierarchy of RL controllers | Personal and community outcomes reconcile; teaching within/between groups is distinguishable |


### Compute feasibility and limits

The 5–10-person range is a proposed engineering starting point, not a measured hardware capacity. Shared weights avoid one model per person, but agent decisions, memories, rollout storage, interactions, and training still add cost. Naive all-pairs interaction checks grow quadratically; use local spatial queries and batching when warranted. Benchmark tick time, decisions/second, training wall time, RAM/VRAM, and reproducibility on the laptop first. The RTX 3060 Ti may help larger batched training later, but no speed, agent-count, or training-time guarantee is made.


### Risks and go/no-go gate

- More moving actors can look convincing while learning, technology trade-offs, and cooperative behavior remain absent.
- Credit assignment and a changing population of learning agents complicate training and debugging.
- The current checkpoint and reward/observation contracts are single-community; old weights must not be silently reused as compatible individual-agent models.
- Require an approved small question that benefits from personal knowledge or cooperation, core resource/action correctness, a reviewed ownership/scheduling contract, and a benchmark plan before F1.
- Individuals need not replace the community-level mode. Keep the tested aggregate prototype as a reference; whether to retain both modes is a future design decision.


### Technical basis · checked 2026-10-10


#### [PettingZoo Parallel API](https://pettingzoo.farama.org/api/parallel/)

Farama Foundation

Official interface and lifecycle guidance reviewed; no integration performed

Supports simultaneous multi-agent action dictionaries and separate observation, reward and termination results. It is a model for an interface, not evidence that ALIVE has implemented it.


#### [RLlib Multi-Agent Environments](https://docs.ray.io/en/latest/rllib/multi-agent-envs.html)

Ray project

Official policy-mapping and variable-sharing guidance reviewed; no integration performed

Documents that multiple agents can map to one policy. Separate personal state/memory and a migration path are our design recommendations, not measured findings from these docs.


## Team & upkeep

One maintained source of truth, linked to code and evidence—not a second set of promises.


### Team context

Existing workbook and meeting notes identify Joao Lucas Veras, Akshay Kumar, and Aryan Dandwekar, with advisor Mahima Agumbe Suresh. These are historical project records; the new task queue deliberately leaves owners unassigned until the team confirms responsibilities.


### Working rhythm

- Before coding: choose a task, confirm owner, scope, dependencies, and completion evidence.
- After each meaningful change: update Current state, append a Journal entry, and reconcile any affected Decision or Roadmap item.
- After an experiment: save the run/configuration and add the conclusion with limitations; never replace evidence with a screenshot alone.
- At team review: resolve blockers, nominate next tasks, and update owners/dates.
- Before advisor review: check that the short pitch, capability inventory, and next milestone agree.
- Keep meetings/ for attendance and meeting-specific action items; summarize material decisions here with source paths.


### Existing meeting convention

meetings/README.md describes weekly team meetings and advisor meetings at least every two weeks. This handbook records that convention; it does not create reminders or confirm that future meetings are scheduled.


### Capture meaningful discussions, not just completed code

The user wants project discussions preserved. After substantive discussions, record the concern or idea, its status (finding, proposal, user preference, or approved decision), implications, evidence/limits, and next step. Put the summary in Journal and update the relevant Vision, Roadmap, Research, or Decisions entry. Preserve disagreements and superseded decisions; do not invent owners, dates, approval, or results. There is no automatic background transcript capture.


### Source library

- Setup and entry point: README.md
- Technical guide: docs/LEVEL_1_GUIDE.md
- Viewer guide: docs/VIEWER_GUIDE.md
- Concept / long-term vision: ALIVE_Technology_Development_Simulation_Concept.md
- Agent design / future mechanics: ALIVE_Agent_Design.md
- Workbook / historical requirements: ALIVE_Workbook_1_Content.md
- Meeting convention: meetings/README.md
- Meeting template: meetings/_template.md
- Earlier comprehensive blueprint · archive; not fully reconciled in this edition: ALIVE_Comprehensive_Project_Blueprint.docx
- Earlier learning/evolution proposal · historical, not automatically active scope: ALIVE_Learning_and_Evolution_Revised_Proposal.docx
- Earlier trait-graph proposal · legacy direction: Trait_Graph_Changing_Worlds_Project_Proposal.docx


### How to maintain and share

- Edit docs/handbook/dist/content.js, the canonical structured content. Navigation, search, website and exports use this same source.
- Run node docs/handbook/build.mjs to validate content and regenerate docs/PROJECT_HANDBOOK.md and docs/handbook/ALIVE_Handbook.html.
- The generated HTML is a standalone offline website: share that one file. Download Markdown and Print / Save PDF are also available in the interface.
- For local preview, run Start_ALIVE_Handbook.ps1. This is a documentation website, not a web version of the simulation.
- No accounts, database, browser status persistence, or simultaneous editing are included. Edits are made in source and reviewed through version control when publishing is authorized.
- The website is not hosted publicly. A later approved deployment can use the buildless dist folder; repository publication is a separate decision.


### Provenance and limits

This consolidation uses the local repository, existing project documents, selected meeting notes, user discussion, paired rule-baseline measurements, the first technology net-ablation, two abstract-level primary papers, and official multi-agent API/policy-sharing guidance. It does not claim a full literature review, new advisor approval, measured RL training success, resolved scarcity balance, isolated per-node causality, or an implemented multi-agent system.
