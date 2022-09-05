from .ecs import Component
from .vector import V2
from dataclasses import dataclass
import pyglet


@dataclass
class ScreenComponent(Component):
    screen: pyglet.window.Window
    viewport_size: V2
    component_name: str = "screen"
    camera_position: V2 = V2(0.0, 0.0)

