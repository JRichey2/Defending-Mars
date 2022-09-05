from .ecs import Component
from dataclasses import dataclass
import pygame
from pygame.math import Vector2 as V2

@dataclass
class PositionComponent(Component):
    component_name: str = "position"
    position: V2 = V2(0.0, 0.0)
    rotate: int = 0
    velocity: V2 = V2(0.0, 0.0)
    z_index: int = 0

