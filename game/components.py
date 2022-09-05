from dataclasses import dataclass, field

import pyglet
from pyglet.sprite import Sprite

from .vector import V2


@dataclass
class InputComponent:
    component_name: str = "input"
    w: bool = False
    a: bool = False
    s: bool = False
    d: bool = False
    q: bool = False
    e: bool = False


@dataclass
class PhysicsComponent:
    component_name: str = "physics"
    position: V2 = V2(0.0, 0.0)
    rotation: int = 0
    velocity: V2 = V2(0.0, 0.0)


class SpriteComponent(Sprite):
    component_name = "sprite"


@dataclass
class WindowComponent:
    window: pyglet.window.Window
    viewport_size: V2
    component_name: str = "window"
    camera_position: V2 = V2(0.0, 0.0)
    background_layers: list[SpriteComponent] = field(default_factory=list)

