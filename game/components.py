from dataclasses import dataclass

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
    z_index: int = 0


@dataclass
class ScreenComponent:
    screen: pyglet.window.Window
    viewport_size: V2
    component_name: str = "screen"
    camera_position: V2 = V2(0.0, 0.0)


class SpriteComponent(Sprite):
    component_name = "sprite"

