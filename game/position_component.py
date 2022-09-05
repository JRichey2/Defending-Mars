from .ecs import Component
from .vector import V2
from dataclasses import dataclass

@dataclass
class PositionComponent(Component):
    component_name: str = "position"
    position: V2 = V2(0.0, 0.0)
    rotate: int = 0
    velocity: V2 = V2(0.0, 0.0)
    z_index: int = 0

