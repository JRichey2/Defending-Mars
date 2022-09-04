from .ecs import Component
from dataclasses import dataclass


@dataclass
class PositionComponent(Component):
    component_name: str = "position"
    x: int = 0
    y: int = 0

