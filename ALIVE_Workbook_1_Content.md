# ALIVE Project Workbook 1 Content

## Team Information

- **Project advisor:** Mahima Agumbe Suresh
- **Team members:**
  - Akshay Kumar
  - Aryan Dandwekar
  - Joao Lucas Veras

## Project Definition

### Proposed Title

**ALIVE: Technology Development and Cultural Diffusion in Artificial Communities**

### Project Description

ALIVE is an artificial-life simulation in which communities occupy a resource-limited environment. Communities gather resources, experiment with new technologies, improve existing technologies, exchange knowledge, and potentially lose technologies when they cannot maintain them. The system will allow users to study how resource availability, technological prerequisites, maintenance costs, and communication between communities affect technological development.

### Primary Research Question

How do resource scarcity, prerequisite relationships, maintenance costs, and knowledge transfer affect the discovery, adoption, spread, and loss of technologies among artificial communities?

### Primary Goals

- Build a reproducible artificial-community simulation.
- Represent technologies using a prerequisite graph.
- Model finite resources and technology-maintenance costs.
- Allow communities to move, gather resources, experiment, and conserve resources.
- Record discoveries, adoption, technological loss, and community outcomes.
- Provide visualization or replay tools for analyzing simulation runs.

> **Scope note:** The repository's older README describes a trait-based artificial-life project. The workbook should consistently use the newer technology-development and cultural-diffusion direction unless the team decides to revert.

---

## 1. Literature Search, State of the Art

### Literature Search

ALIVE draws from research in artificial life, digital evolution, cultural evolution, social learning, network diffusion, and multi-agent systems. Together, these areas provide the academic foundation for a simulation in which resource-limited communities discover, use, exchange, maintain, and sometimes lose technologies.

Digital-evolution platforms demonstrate how artificial populations can be studied through controlled computational experiments. Avida provides configurable experimental conditions, detailed measurements, and post-processing tools for populations of evolving computer programs (Ofria & Wilke, 2004). Contemporary artificial-life research has expanded beyond individual digital organisms to include artificial societies, ecosystems, collective behavior, emergence, and open-ended systems (Dorin & Stepney, 2024). These works support ALIVE's use of repeatable scenarios, measurable outcomes, and observable artificial communities.

Research on cultural and technological evolution supports ALIVE's technology-development model. Wagner and Rosen (2014) describe technological innovation as movement through a space of possible discoveries shaped by trial and error, existing designs, and horizontal information transfer. Borg et al. (2024) describe human culture as an evolutionary system capable of cumulative change and continuing novelty. These concepts correspond to ALIVE's prerequisite-based technology graph, in which earlier discoveries make later technologies reachable and knowledge can accumulate across time.

Social-learning research addresses the choice between independent experimentation and learning from others. Hinton and Nowlan (1987) show that learning during a lifetime can influence longer-term adaptive processes. Rendell et al. (2010) compare simulated strategies that innovate, observe others, or exploit existing knowledge in a changing environment. Their work supports separate ALIVE actions for experimentation, knowledge exchange, and use of acquired technologies.

Communication structure affects how discoveries spread and whether diversity persists. Axelrod (1997) demonstrates that local cultural influence can produce convergence within groups while maintaining differences across a larger population. Derex and Boyd (2016) show that partial connectivity can preserve alternative solutions that are later combined into more complex outcomes. Lazer and Friedman (2007) similarly describe a tradeoff between rapid diffusion of successful ideas and preservation of the diversity needed for long-term exploration. These studies support configurable communication ranges and contact networks between ALIVE communities.

Resource conditions can also change social behavior. Leibo et al. (2017) use sequential social dilemmas to demonstrate that environmental conditions, including resource abundance, influence whether learning agents behave cooperatively or competitively. ALIVE applies this idea by making resources necessary for survival, experimentation, construction, and technology maintenance. The academic literature therefore supports the project's core variables: resources, technology prerequisites, independent discovery, social transmission, network connectivity, environmental change, and measurable simulation outcomes.

### State-of-the-Art Summary

The state of the art for artificial-community simulation uses modular open-source tools rather than a single platform. Mesa provides established components for agent-based models, including spatial environments, activation, data collection, repeated experiments, and browser-based visualization (Mesa Project, n.d.). PettingZoo supplies standard interfaces for turn-based and simultaneous multi-agent environments, allowing a simulator to work with external learning tools without depending on one algorithm (Farama Foundation, n.d.).

Several specialized tools could support ALIVE's advanced features. RLlib offers scalable multi-agent reinforcement learning and supports both shared and separate agent policies (Ray Team, n.d.). JAX provides just-in-time compilation, automatic vectorization, and execution on CPUs, GPUs, and TPUs, which could accelerate large batches of simulation runs after the basic engine is validated (JAX Authors, n.d.). NetworkX provides directed-graph algorithms that can validate prerequisites, detect cycles, determine reachable technologies, and analyze communication networks (NetworkX Developers, 2026).

Interactive and reproducible analysis is also standard in modern simulation systems. Plotly can present technology graphs, resource histories, discovery timelines, adoption rates, and comparisons between communities through interactive charts and standalone reports (Plotly Technologies Inc., n.d.). These views should be supported by deterministic random seeds, configuration files, structured event logs, and repeatable experiment runs.

For ALIVE, the recommended approach is a modular Python simulation with a PettingZoo-style interface, a directed technology graph, reproducible scenarios, event logging, and interactive analysis. Mesa can serve as an agent-based-modeling reference, NetworkX and Plotly can support graph analysis and visualization, and JAX or RLlib can be introduced later if performance testing or learned-agent experiments require them. This approach provides modern capabilities while keeping the initial system understandable and testable.

### References

Axelrod, R. (1997). The dissemination of culture: A model with local convergence and global polarization. *Journal of Conflict Resolution, 41*(2), 203–226. https://doi.org/10.1177/0022002797041002001

This source models how local cultural imitation can create similarity within communities while preserving differences between them, informing ALIVE's knowledge-exchange mechanics.

Borg, J. M., Buskell, A., Kapitany, R., Powers, S. T., Reindl, E., & Tennie, C. (2024). Evolved open-endedness in cultural evolution: A new dimension in open-ended evolution research. *Artificial Life, 30*(3), 417–438. https://doi.org/10.1162/artl_a_00406

This source describes culture as an evolving system that generates cumulative novelty and complexity, supporting ALIVE's technology-progression concept.

Derex, M., & Boyd, R. (2016). Partial connectivity increases cultural accumulation within groups. *Proceedings of the National Academy of Sciences of the United States of America, 113*(11), 2982–2987. https://doi.org/10.1073/pnas.1518798113

This source shows how partial connectivity can preserve diverse discoveries and promote cumulative innovation across communities.

Dorin, A., & Stepney, S. (2024). What is artificial life today, and where should it go? *Artificial Life, 30*(1), 1–15. https://doi.org/10.1162/artl_e_00435

This source surveys modern artificial-life research and places artificial societies and virtual environments within the field containing ALIVE.

Farama Foundation. (n.d.). *PettingZoo documentation*. Retrieved September 30, 2026, from https://pettingzoo.farama.org/

This source defines standard interfaces for sequential and simultaneous multi-agent environments that can guide ALIVE's external API.

Hinton, G. E., & Nowlan, S. J. (1987). How learning can guide evolution. *Complex Systems, 1*, 495–502. https://www.cs.toronto.edu/~hinton/absps/evolution.htm

This source demonstrates how individual learning can influence longer-term evolution, providing background for learning and inherited knowledge in ALIVE.

JAX Authors. (n.d.). *JAX: High performance array computing*. Retrieved September 30, 2026, from https://docs.jax.dev/en/latest/

This source describes compiled and vectorized numerical computing that could accelerate large batches of ALIVE simulations.

Lazer, D., & Friedman, A. (2007). The network structure of exploration and exploitation. *Administrative Science Quarterly, 52*(4), 667–694. https://doi.org/10.2189/asqu.52.4.667

This source explains how network connectivity creates a tradeoff between rapid knowledge sharing and preserving diversity for exploration.

Leibo, J. Z., Zambaldi, V. F., Lanctot, M., Marecki, J., & Graepel, T. (2017). Multi-agent reinforcement learning in sequential social dilemmas. In K. Larson, M. Winikoff, S. Das, & E. Durfee (Eds.), *Proceedings of the 16th Conference on Autonomous Agents and MultiAgent Systems* (pp. 464–473). International Foundation for Autonomous Agents and Multiagent Systems. https://arxiv.org/abs/1702.03037

This source examines how resource conditions influence cooperation and competition among learning agents, supporting ALIVE's scarcity mechanics.

Mesa Project. (n.d.). *Mesa: Agent-based modeling in Python*. Retrieved September 30, 2026, from https://mesa.readthedocs.io/stable/

This source describes a modern Python framework for agent behavior, spatial simulation, data collection, repeated experiments, and visualization.

NetworkX Developers. (2026). *NetworkX 3.7 documentation*. https://networkx.org/documentation/stable/

This source documents graph structures and algorithms applicable to ALIVE's technology prerequisites and communication networks.

Ofria, C., & Wilke, C. O. (2004). Avida: A software platform for research in computational evolutionary biology. *Artificial Life, 10*(2), 191–229. https://doi.org/10.1162/106454604773563612

This source describes a repeatable digital-evolution platform that provides a methodological reference for ALIVE's experiments and measurements.

Plotly Technologies Inc. (n.d.). *Getting started with Plotly in Python*. Retrieved September 30, 2026, from https://plotly.com/python/getting-started/

This source documents interactive visualizations suitable for ALIVE's technology graphs, resource histories, timelines, and experiment comparisons.

Ray Team. (n.d.). *Multi-agent environments*. Retrieved September 30, 2026, from https://docs.ray.io/en/latest/rllib/multi-agent-envs.html

This source describes scalable multi-agent policy training and PettingZoo integration for possible future learned-agent experiments.

Rendell, L., Boyd, R., Cownden, D., Enquist, M., Eriksson, K., Feldman, M. W., Fogarty, L., Ghirlanda, S., Lillicrap, T., & Laland, K. N. (2010). Why copy others? Insights from the social learning strategies tournament. *Science, 328*(5975), 208–213. https://doi.org/10.1126/science.1184719

This source compares innovation, observation, and exploitation strategies that correspond to ALIVE's experimentation and technology-sharing actions.

Wagner, A., & Rosen, W. (2014). Spaces of the possible: Universal Darwinism and the wall between technological and biological innovation. *Journal of the Royal Society Interface, 11*(97), Article 20131190. https://doi.org/10.1098/rsif.2013.1190

This source connects technological innovation with trial and error, independent discovery, and information transfer, supporting ALIVE's technology graph.

---

## 2. Project Justification

Existing artificial-life and multi-agent systems frequently concentrate on biological evolution, competitive performance, or learned policies. These systems may demonstrate complex behavior but can make the actual process of cumulative technological development difficult to observe. ALIVE addresses this problem by representing technologies explicitly as discoveries with prerequisites, resource costs, benefits, proficiency levels, and maintenance requirements.

The project is useful because it gives researchers, students, and developers a controlled environment for examining how technologies emerge and spread. Users will be able to change environmental abundance, the structure of the technology graph, communication opportunities, and maintenance costs and then compare the resulting community behavior. Unlike an unrestricted machine-learning model, the intended design makes important events explainable through logs, metrics, and replayable simulation histories.

The project is feasible because it can be implemented incrementally. A minimum version requires only a grid environment, resources, community states, a small technology graph, baseline decision policies, and an event log. More advanced features, such as trade, reinforcement learning, conflict, and GPU acceleration, can be added after the core simulation works.

---

## 3. Requirements

### Essential Functional Requirements

The system shall:

- Create a configurable environment with finite resources.
- Represent multiple communities with positions and resource inventories.
- Provide communities with legal actions based on their current state.
- Support movement, gathering, experimentation, and conservation actions.
- Represent technologies using a directed prerequisite graph.
- Prevent a technology from being discovered before its prerequisites are met.
- Associate technologies with costs, effects, and maintenance requirements.
- Track each community's technology progress or proficiency.
- Apply resource consumption and technology effects during simulation steps.
- Support deterministic seeded runs.
- Record important events, including discoveries, adoption, resource shortages, and technological loss.
- Export simulation results for later analysis.

### Desired Requirements

- Scenario configuration files.
- Baseline community policies.
- Technology sharing or trade.
- Interactive visualization.
- Simulation replay.
- Checkpoints for long experiments.
- Comparison of multiple experimental runs.
- Configurable resource regeneration.
- Graphical display of the technology tree.

### Optional Requirements

- Reinforcement-learning agents.
- Alliances or conflict between communities.
- Migration and population growth.
- Environmental disasters.
- Large-scale GPU execution.
- User-created technology graphs.
- Automated parameter searches.

### Nonfunctional Requirements

- **Reproducibility:** Identical configurations and seeds should produce identical results.
- **Modularity:** Environment, technology, policy, logging, and visualization code should remain separate.
- **Validation:** Invalid technology graphs and configurations should be rejected.
- **Performance:** The simulator should support multiple communities and repeated experiments without excessive runtime.
- **Testability:** Resource accounting and technology prerequisites should have automated tests.
- **Usability:** Users should be able to run a basic scenario without modifying source code.
- **Portability:** The basic simulation should operate on ordinary CPU hardware.

### Suggested Acceptance Criteria

- A seeded simulation can be repeated with matching results.
- At least three communities can run in the same environment.
- The demonstration technology graph contains at least 8–12 technologies.
- A community cannot unlock a technology without its prerequisites.
- Simulation output reports discovery time, adoption rate, resource level, technology loss, and community survival.
- A complete run can be replayed or reconstructed from its saved log.

---

## 4. Dependencies and Deliverables

### Critical Dependencies

| Dependency | Why It Matters | Mitigation |
|---|---|---|
| Finalized project scope | Architecture and requirements depend on it | Freeze the minimum viable scope before expanding features |
| Technology graph design | Determines discovery and progression mechanics | Begin with a small validated graph |
| Hardware availability | Large batches or learning experiments may need acceleration | Make the baseline simulation CPU-compatible |
| Python/JAX compatibility | Accelerator support varies by platform | Keep core logic independent of optional JAX acceleration |
| Advisor approval | Prevents development in the wrong direction | Review requirements and architecture early |
| Team availability | Integration requires coordinated contributions | Assign owners and review progress weekly |

JAX's official [installation documentation](https://docs.jax.dev/en/latest/installation.html) notes that accelerator support differs by operating system and hardware. GPU execution should therefore not be a required dependency for the first version.

### Deliverables

1. Written requirements and project architecture.
2. Configurable artificial-community simulation.
3. Validated technology prerequisite graph.
4. Resource and community-state models.
5. Baseline agent or community policies.
6. Event logging and experiment metrics.
7. Simulation visualization or replay tool.
8. Example scenarios and configuration files.
9. Automated tests.
10. Technical documentation and setup instructions.
11. Final demonstration and results report.

---

## 5. Architecture

### System Flow

```text
Scenario Configuration
        |
        v
Simulation Controller
        |
        v
World State -> Community Observations -> Community Policies
    ^                                      |
    |                                      v
Event Log <- Action Resolver <- Legal Action Mask
    |
    v
Replay, Metrics, and Visualization
```

### Component Responsibilities

- **Scenario configuration:** Defines map size, resources, communities, technology graph, seed, and run length.
- **Simulation controller:** Starts, pauses, advances, and terminates a run.
- **World state:** Stores resource locations, community positions, inventories, and technology progress.
- **Technology graph:** Validates prerequisites and applies technology costs and effects.
- **Observation system:** Exposes only the information available to each community.
- **Policy system:** Selects actions using a baseline rule-based policy or, later, a learned policy.
- **Action resolver:** Validates and applies movement, gathering, experimentation, conservation, and sharing actions.
- **Event logger:** Records state changes and important discoveries.
- **Analysis layer:** Calculates metrics and supports visualization or replay.

### Recommended Technology Choices

- Python for the simulator and supporting tools.
- Dataclasses or equivalent models for clearly defined simulation state.
- JSON or YAML for scenarios.
- CSV or JSON Lines for event logs.
- GitHub for source control.
- Automated Python tests for validation.
- JAX only where profiling demonstrates a performance benefit.
- PettingZoo-style interfaces if reinforcement-learning compatibility is added.

---

## 6. Implementation Plan

### Work Already Represented in the Repository

The initial codebase contains:

- Resource and position models.
- Community inventories and state models.
- Technology progress models.
- World-configuration structures.
- Technology definitions and prerequisite-graph validation.
- Technology maintenance costs and effects.
- Action definitions for movement, gathering, experimentation, and conservation.
- Action encoding, decoding, and legal-action masks.

These pieces are a foundation and do not yet represent a complete simulator.

### Remaining Implementation Order

1. Finalize the minimum technology graph.
2. Implement world initialization and resource placement.
3. Implement the simulation-step and action-resolution engine.
4. Add resource consumption and regeneration.
5. Apply technology effects and maintenance.
6. Implement a baseline community policy.
7. Add event logging and experiment metrics.
8. Add technology sharing or diffusion.
9. Build visualization and replay.
10. Add automated tests and example scenarios.
11. Profile the program before introducing GPU acceleration.
12. Run validation experiments and prepare the demonstration.

### Risks

- Excessively large scope.
- Technology rules becoming too complicated.
- Communities becoming inactive because actions are poorly balanced.
- Hardware acceleration distracting from the core simulator.
- Inconsistent terminology across the README, workbook, and code.
- Insufficient tests for resource accounting and prerequisites.

---

## 7. Proposed Project Schedule

The following dates are a proposed starting point and must be adjusted to the course's actual semester deadlines.

| Period | Project Work | Primary Owner |
|---|---|---|
| Sep. 29–Oct. 4 | Freeze scope, requirements, literature, and architecture | Akshay |
| Oct. 5–11 | Complete world initialization and resource mechanics | Joao |
| Oct. 12–18 | Implement action resolution and simulation loop | Joao |
| Oct. 19–25 | Complete technology graph and technology effects | Akshay |
| Oct. 26–Nov. 1 | Implement baseline community policies | Akshay and Joao |
| Nov. 2–8 | Add event logging, metrics, and experiment configuration | Aryan |
| Nov. 9–15 | Add technology sharing and diffusion | Aryan |
| Nov. 16–22 | Build visualization and replay | Aryan and Joao |
| Nov. 23–29 | Integration testing and performance measurement | All members |
| Nov. 30–Dec. 6 | Run experiments and analyze results | All members |
| Final week | Documentation, demonstration, and final submission | All members |

Class assignments such as completing the workbook should not be the main entries in the project schedule. The schedule should primarily show actual development work.

---

## Team Contribution Statement

- **Akshay Kumar:** Literature review, requirements, technology-graph design, baseline-policy development, and workbook coordination.
- **Aryan Dandwekar:** Scenario configuration, event logging, diffusion mechanics, experiment execution, replay support, and advisor coordination.
- **Joao Lucas Veras:** Simulation engine, action resolution, code integration, automated testing, and performance evaluation.
- **All members:** Architectural review, integration testing, analysis, documentation, and final presentation.

---

## Information the Team Must Confirm

Before calling the workbook complete, the team must agree on:

- [ ] The exact minimum set of technologies.
- [ ] Whether technology sharing is required for the first demonstration.
- [ ] Whether communities use rule-based, learned, or both types of policies.
- [ ] The size and duration of the demonstration scenario.
- [ ] The measurable performance target.
- [ ] The final semester milestones.
- [ ] Whether the advisor approves the architecture and project scope.
- [ ] Which member wrote or reviewed each workbook section.
- [ ] The required citation style and minimum number of sources.
- [ ] The final architecture figure.

Once those decisions are recorded, properly formatted references and the final architecture figure can be added to complete the workbook content.
