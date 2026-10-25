"""Fixed, named observation features shared by baselines and RL.

Only self state and the visible Manhattan neighborhood are exposed. Unknown
cells use a visibility flag so zero resource amount is not confused with unseen.
Normalization uses fixed scales, never hidden episode-wide resource statistics.
"""

from dataclasses import dataclass
from .models import Position, Resource
from .world import GridWorld, WorldState


@dataclass(frozen=True)
class Observation:
    values: tuple[float, ...]
    names: tuple[str, ...]
    action_mask: tuple[bool, ...]

    def as_dict(self) -> dict[str, float]:
        return dict(zip(self.names, self.values))


def observe(world: GridWorld, state: WorldState) -> Observation:
    world.validate_state(state)
    c, cfg = state.community, world.config
    features = {
        "x": c.position.x / (cfg.width - 1),
        "y": c.position.y / (cfg.height - 1),
        "time": state.step / cfg.max_steps,
        "population": min(c.population / cfg.starting_population, 1.0),
        "labor": min(c.available_labor / cfg.starting_population, 1.0),
    }
    for resource in Resource:
        amount = c.resources.amount(resource)
        features[resource.value] = amount / (amount + 30.0)
    for tid in world.technology_graph.topological_ids():
        p = c.technology(tid)
        features[f"tech:{tid}:progress"] = p.discovery_progress if p else 0.0
        features[f"tech:{tid}:active"] = float(p.active) if p else 0.0
    radius = cfg.observation_radius
    visible = {d.key: d for d in world.visible_deposits(state)}
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            pos = Position(c.position.x + dx, c.position.y + dy)
            seen = abs(dx) + abs(dy) <= radius and cfg.contains(pos)
            prefix = f"cell:{dx}:{dy}"
            features[f"{prefix}:visible"] = float(seen)
            for resource in Resource:
                d = visible.get((pos, resource)) if seen else None
                amount = d.amount if d else 0.0
                features[f"{prefix}:{resource.value}"] = amount / (amount + 30.0)
    for label in world.action_catalog.labels:
        features[f"previous:{label}"] = float(c.previous_action == label)
    return Observation(tuple(features.values()), tuple(features),
                       world.legal_action_mask(state).values)
