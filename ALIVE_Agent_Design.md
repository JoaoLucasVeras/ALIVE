# ALIVE Agent Design

## Purpose

This document describes how agents will work in **ALIVE - Adaptive Life in Virtual Environments**.

In this version of ALIVE, an agent represents an **abstract community or social group**. It does not represent one individual person, a real culture, ethnicity, country, or historical civilization.

Each agent will:

- Observe part of the simulated world
- Track its resources, technologies, population, and relationships
- Choose from actions that are currently available
- Experience the consequences of those actions
- Learn from recent successes and failures
- Discover, adopt, improve, share, or lose technologies
- Grow, decline, relocate, split, or collapse

An agent does not need human-level intelligence. Believable behavior can emerge from groups repeatedly making limited decisions under changing conditions.

## Core idea

An agent consists of two things:

1. **Agent state:** everything the group currently has, knows, remembers, and believes.
2. **Decision policy:** the process used to select the group's next action.

The simulation engine controls the world and applies the consequences. Agents can only attempt actions that the engine defines.

```text
World and nearby groups
          |
          v
      Observation
          |
          v
  Agent decision policy
          |
          v
    Selected action
          |
          v
Simulation resolves action
          |
          v
Resources, knowledge, relationships,
population, and memory are updated
```

## What an agent contains

Each community agent should store the following state.

### Identity and location

- Unique group ID
- Display name
- Current map position
- Optional group color or symbol
- Whether the group is active or extinct

### Population and capacity

- Current population
- Available labor
- Carrying or storage capacity
- Health or stability level
- Growth and decline history

Population does not need to simulate every individual person. It can be a number representing the size and productive capacity of the community.

### Resources

The first version could use:

- Food
- Wood
- Stone

Later versions could add water, metals, fuel, medicine, tools, or abstract labor.

For every resource, the agent may track:

- Current amount
- Storage capacity
- Recent income
- Recent consumption
- Expected shortage

### Technology knowledge

For each technology, an agent may have one of several states:

- Unknown
- Partially understood
- Known
- Practiced
- Temporarily unavailable because requirements are missing
- Lost

The first implementation can simplify this to:

```text
known: true or false
proficiency: number from 0 to 1
```

### Relationships

Each group may store information about every group it has encountered:

- Trust
- Hostility
- Familiarity
- Recent trades
- Recent technology exchanges
- Unpaid obligations
- Current partnership status

Relationships should be directed. The River Group may trust the Hill Group even if the Hill Group does not trust the River Group.

### Needs and priorities

Priorities are calculated from the current state rather than written as permanent personalities.

Examples include:

- Avoid starvation
- Prepare for expected scarcity
- Increase storage
- Discover a missing prerequisite
- Obtain a nearby resource
- Improve a trusted relationship
- Protect a technological advantage
- Relocate from an unproductive area

### Lifetime or group memory

An agent can remember recent outcomes such as:

- Gathering food succeeded
- Experimenting consumed resources without a discovery
- Trading with a neighboring group was beneficial
- Sharing a technology increased trust
- A recipient later became a competitor
- A location repeatedly produced few resources

Memory should be limited. Recent events can have more influence than older events so that agents can adjust when the world changes.

## Example agent state

```yaml
id: group_river
name: River Group
position: [12, 8]
active: true

population: 42
available_labor: 24

resources:
  food: 30
  wood: 70
  stone: 12

technologies:
  fire:
    known: true
    proficiency: 0.85
  cooking:
    known: true
    proficiency: 0.60
  wheel:
    known: false
    progress: 0.25

relationships:
  group_hill:
    trust: 0.80
    hostility: 0.05
  group_lake:
    trust: 0.20
    hostility: 0.40

recent_memory:
  - action: gather_food
    result: success
    value: 4.5
  - action: trade_stone
    result: failure
    value: -2.0
```

## What an agent can observe

Agents should not automatically know everything in the world. Each agent receives a limited observation based on its position, technologies, and relationships.

An observation may include:

- The agent's own resources and population
- Resources in nearby map cells
- Nearby groups
- Known relationships
- Visible actions by other groups
- Technologies intentionally shared with it
- Recent environmental changes
- Its own recent action outcomes

Technologies can improve observation. For example, navigation may increase exploration range, record keeping may improve memory, and communication may improve knowledge received from other groups.

The system should distinguish the true world state from what an agent knows:

```text
True world state -> observation function -> agent's limited information
```

This makes discovery, uncertainty, communication, and misinformation possible later.

## Available actions

The first version should use a small action set.

### Gather

The group collects a nearby resource.

Requirements may include:

- Resource is visible and reachable
- Labor is available
- Required tools are known

Possible consequences:

- Resources increase
- Labor or energy is spent
- The local resource is reduced
- Technology proficiency improves

### Move

The group relocates or explores another location.

Possible consequences:

- Movement consumes food or labor
- New resources become visible
- New groups are encountered
- Old trading relationships become harder to use

### Experiment

The group invests resources in discovering or improving a technology.

Requirements may include:

- Required prerequisites are known
- Required resources are available
- Enough labor or time is available

Possible consequences:

- Discovery progress increases
- A new technology is unlocked
- Resources are consumed without success
- Experience makes later attempts easier

### Adopt

The group learns a technology that it has observed or received from another group.

Adoption should not always be automatic. It may require:

- Existing prerequisite knowledge
- Time and resources
- Sufficient contact with the source group
- Compatibility with current technologies

### Share

The group attempts to teach a known technology to another group.

Possible consequences:

- The recipient gains discovery progress or knowledge
- Trust increases
- The sender pays time or resource costs
- The recipient becomes a stronger partner
- The recipient becomes a stronger competitor
- The technology spreads beyond the intended recipient

### Trade

Two groups exchange resources or knowledge.

Possible consequences:

- Both groups benefit
- One group receives a better deal
- Trust changes
- New technologies become observable
- A trade network develops

### Contest

A group tries to gain control of a resource or location.

Possible consequences:

- Resources change ownership
- Both groups pay a cost
- Population or stability decreases
- Hostility increases
- Technologies affect the probability and cost of success

Contest can be omitted from the earliest prototype if it distracts from technology sharing.

### Conserve

The group reduces activity to preserve resources.

Possible consequences:

- Consumption decreases
- Discovery and growth slow down
- The group survives a short crisis
- Other groups gain opportunities while it remains inactive

### Split or establish a settlement

A sufficiently large group may create a new community.

Possible consequences:

- Population and resources are divided
- The new group inherits some technologies
- Relationships begin similar but can diverge
- The new group occupies a different location
- Knowledge can be lost during the split

This is the cultural-development equivalent of reproduction in the earlier ALIVE design.

## How the agent decides

The recommended first decision system is a **utility-based policy**.

The policy performs four steps:

1. Generate the actions that are currently legal.
2. Estimate the usefulness of each action.
3. Adjust those estimates using memory and relationships.
4. Select an action, including limited randomness.

An action score could combine:

```text
action score =
    immediate need benefit
  + expected resource benefit
  + technology opportunity
  + relationship benefit
  + learned preference
  - resource cost
  - risk
  - delay cost
```

Example scores:

```text
Gather food:       8.5
Trade for food:    7.0
Experiment:        4.5
Share technology:  3.0
Move:              2.5
Contest resource:  1.0
```

The agent usually chooses a high-scoring action. A small amount of randomness allows exploration and prevents every run from producing the same history.

## Rule-based starting policy

The first prototype can use understandable rules:

```text
If food is critically low:
    prefer gathering, trading for food, or conserving

If local resources remain poor:
    prefer exploration or movement

If resources are stable:
    consider experimentation

If another group is trusted:
    increase the value of trade and sharing

If another group recently caused harm:
    decrease the value of sharing and trade

If a useful technology is almost discovered:
    increase the value of experimentation
```

This approach makes decisions easy to inspect and explain.

## How the agent learns

Agents can learn by updating preferences after actions succeed or fail.

Each action or behavior category has a learned value:

```text
explore:     0.20
gather:      0.75
experiment:  0.40
share:       0.10
trade:       0.65
conserve:    0.30
```

After an action, the agent receives a reward based on its outcome. A simple update is:

```text
new value = old value + learning rate * (reward - old value)
```

Examples of possible reward components:

- Resources gained
- Shortage avoided
- Population maintained
- Technology progress
- Relationship improvement
- Costs paid
- Resources lost
- Population decline

The design must avoid treating every immediate resource loss as failure. Experimentation, movement, sharing, and storage can have delayed benefits. Actions can therefore be evaluated over a short outcome window instead of only during the step when they occur.

Older learned values should gradually move toward their starting values. This prevents one early event from controlling the group forever.

## Technology discovery and adoption

The technology graph defines the possible technologies and their relationships.

Example technology configuration:

```yaml
wheel:
  category: transport
  prerequisites:
    - basic_tools
    - woodworking
  discovery_cost:
    wood: 20
    labor: 10
  maintenance_cost:
    wood: 1
  effects:
    transport_capacity_multiplier: 2.0
    movement_cost_multiplier: 0.75
  unlocks:
    - cart
  sharing_difficulty: 0.35
```

Technology can enter a group through:

- Independent experimentation
- Teaching
- Trade
- Observation and imitation
- Knowledge inherited after a group splits
- A later optional mechanism such as merging or conquest

Technology adoption may take several turns. This prevents a single sharing action from instantly giving the recipient full capability.

## Technology loss

Knowledge should not necessarily remain forever.

A group may lose access to a technology when:

- Its population becomes too small
- Required specialists or resources disappear
- A prerequisite technology is lost
- The technology is not used for a long time
- Maintenance becomes too expensive
- A group splits and knowledge is unevenly distributed

The group could retain partial knowledge, making rediscovery easier than the original discovery.

## Relationships and sharing decisions

A group should evaluate both the immediate and possible future consequences of sharing.

The value of sharing may depend on:

- Trust in the recipient
- Expected return benefit
- Current resource scarcity
- Whether the technology is cooperative or competitive
- Whether the recipient can share it again
- The recipient's current strength
- Geographic proximity
- Recent help or harm

For example, sharing storage may keep a trading partner alive during scarcity. Sharing weapons may also protect an ally, but could create a stronger future rival.

The system should record the source and path of each transfer:

```text
River Group -> Hill Group -> Lake Group
Technology: Fire
Transfer type: Teaching, then imitation
```

## Growth, decline, splitting, and collapse

Group population changes according to resource stability and environmental pressure.

Possible rules include:

- Sustained resource surplus produces gradual growth.
- Shortage produces decline.
- Severe shortage can cause collapse.
- Technologies change production, storage, and consumption.
- A large and stable group may split or create a settlement.

When a group splits:

- Population and resources are divided.
- A configurable portion of technology is inherited.
- Learned action preferences may partially transfer as cultural knowledge.
- The new settlement receives a new identity.
- Both groups can develop independently afterward.

Unlike biological reproduction, cultural knowledge can pass between unrelated groups. Splitting is therefore only one source of technological inheritance.

## One complete simulation turn

Every simulation turn should follow a consistent sequence:

1. Apply scheduled environmental changes.
2. Regrow or move environmental resources.
3. Build a limited observation for every active group.
4. Generate legal actions for every group.
5. Let each group's policy select an intended action.
6. Resolve intended actions using a fair simultaneous process.
7. Update resources, population, technologies, and relationships.
8. Calculate delayed outcomes and learning rewards.
9. Update group memory and learned preferences.
10. Process growth, splitting, and collapse.
11. Record events and summary measurements.
12. Update the visualization.

Actions should be resolved simultaneously or through a seeded conflict-resolution rule. The order of groups in an array should not determine who wins.

## Example turn

Consider two communities:

- The River Group knows fire and fishing.
- The Hill Group knows stone tools and storage.

A drought reduces food around the river.

1. The River Group observes declining food.
2. It considers gathering, moving, experimenting, trading, and contesting.
3. It remembers that previous trades with the Hill Group were beneficial.
4. It offers fishing knowledge in exchange for storage knowledge.
5. The Hill Group accepts because fishing provides another food source.
6. Both groups pay a teaching and adoption cost.
7. Trust increases and both technologies begin spreading.
8. The River Group later survives scarcity by storing food.
9. The Hill Group later uses fishing to compete for river resources.

Sharing initially helps both groups while also creating future competition. This kind of delayed consequence is one of the main behaviors ALIVE should make visible.

## Levels of agent intelligence

### Level 1: Scripted rules

Agents follow understandable utility rules. This is the recommended minimum viable version because it is easy to test and explain.

### Level 2: Learned action preferences

Agents adjust action values from recent outcomes. Different groups can develop different strategies even when they begin with the same rules.

### Level 3: Planning

Agents estimate several possible future steps before choosing an action. This may support investment, alliances, and delayed technology benefits.

### Level 4: Reinforcement-learning policies

Policies are trained across many simulations. These agents may discover strategies the developers did not explicitly program, but they are harder to explain and validate.

Large language models are not required for the core system. They could later generate readable explanations or scenario text, but the simulation's decisions and state changes should remain structured and reproducible.

## Software architecture

```text
Technology definitions
          |
          v
World state -> Observation system -> Agent policy
     ^                               |
     |                               v
History <- Outcome and learning <- Action resolver
     |
     v
Visualization and analysis
```

### World engine

Responsible for:

- Map cells
- Resource quantities
- Resource regeneration
- Environmental schedules
- Movement and distance

### Agent state

Responsible for:

- Population
- Stored resources
- Known technologies
- Relationships
- Memory
- Learned preferences

### Technology graph

Responsible for:

- Technology definitions
- Prerequisites
- Costs
- Effects
- Compatibility
- Discovery and sharing rules

### Decision engine

Responsible for:

- Generating legal actions
- Scoring actions
- Applying learned preferences
- Selecting an action

### Action resolver

Responsible for:

- Applying costs and benefits
- Resolving interactions fairly
- Updating shared resources
- Handling trades and technology transfers
- Producing structured outcomes

### History and explanation system

Responsible for:

- Recording major events
- Tracking the source of technologies
- Explaining why an action was selected
- Supporting replay and comparison

### Visualization

Responsible for displaying:

- Groups on the map
- Resources and environmental changes
- Known technologies
- Relationships and exchanges
- Technology transfers
- Population and resource histories
- Important event notifications

## Explainable decisions

The system should save the factors that contributed to every selected action.

Example:

```text
Selected action: Trade for food

Reasons:
  Food shortage:              +5.0
  Trusted neighbor nearby:    +2.0
  Previous successful trade:  +1.5
  Trade cost:                 -0.5
  Total score:                 8.0
```

These explanations will make the simulation easier to debug and more meaningful to users.

## Recommended first prototype

The initial prototype should contain:

- Four community agents
- One two-dimensional map
- Three resources: food, wood, and stone
- Eight to twelve technologies
- Five primary actions: gather, move, experiment, trade, and share
- A simple utility-based decision policy
- Limited action-preference learning
- Trust between groups
- One stable and one scarcity environment
- Event history and deterministic replay from a saved seed

Contest, group splitting, advanced planning, and a large technology graph can follow after the basic loop works.

## Minimum implementation order

1. Create the world grid and resource system.
2. Represent agent state without any decision-making.
3. Implement gather and move actions.
4. Add the technology graph and experiment action.
5. Add multiple groups and simultaneous action resolution.
6. Implement trade and technology sharing.
7. Add relationships and trust updates.
8. Add the utility-based policy.
9. Add limited learning and memory.
10. Add event logging, explanations, and replay.
11. Add visualization.
12. Validate the complete small scenario before expanding.

## Validation questions

Before adding more intelligence or technologies, verify:

- Can a group survive by gathering basic resources?
- Does a technology produce its stated benefit and cost?
- Are prerequisite rules enforced?
- Can technology be independently discovered?
- Can technology be shared and adopted?
- Is every technology transfer traceable?
- Do relationships change after beneficial and harmful actions?
- Can learning change future decisions?
- Can agents recover when the environment changes?
- Are results reproducible when the same random seed is used?
- Does changing the order of agents leave the outcome rules fair?
- Can the interface explain why each major action occurred?

## Design principles

- Keep agents abstract and avoid claims about real cultures.
- Begin with transparent rules before adding complex learning.
- Give agents limited information.
- Make every technology benefit carry a cost, dependency, or risk.
- Allow multiple technological paths where possible.
- Keep agent decisions separate from action consequences.
- Resolve interactions fairly and reproducibly.
- Record why actions were selected and what happened afterward.
- Validate a small complete system before expanding the technology graph.
- Treat emergent outcomes as consequences of the programmed model assumptions.

## Agent summary

An ALIVE agent is an abstract community with resources, population, technologies, relationships, limited observations, and memory. A decision policy scores its available actions. The simulation engine resolves those actions and returns their consequences. The agent learns from those results, while technologies alter what actions are possible and how effective they are.

The simulation comes to life through the repeated loop:

> **Observe -> decide -> act -> experience consequences -> learn -> repeat**

When several communities perform this loop together in a changing world, technological development, cooperation, competition, specialization, and knowledge diffusion can emerge from their interactions.
