from .ecs import Component
from dataclasses import dataclass
from pygame import Surface
from pygame.math import Vector2 as V2


@dataclass
class ScreenComponent(Component):
    screen: Surface
    background: Surface
    viewport_size: V2
    component_name: str = "screen"
    camera_position: V2 = V2(0.0, 0.0)

