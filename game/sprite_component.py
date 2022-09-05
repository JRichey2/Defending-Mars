from .ecs import Component
from dataclasses import dataclass
from pyglet.sprite import Sprite

@dataclass
class SpriteComponent(Component):
    sprite: Sprite
    component_name: str = "sprite"
    scale: float = 1.0

