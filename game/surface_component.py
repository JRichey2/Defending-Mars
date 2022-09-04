from .ecs import Component
from dataclasses import dataclass
from pygame import Surface

@dataclass
class SurfaceComponent(Component):
    surface: Surface
    component_name: str = "surface"
