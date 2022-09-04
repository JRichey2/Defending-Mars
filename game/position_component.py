from .ecs import Component
from dataclasses import dataclass
import pygame

@dataclass
class PositionComponent(Component):
    component_name: str = "position"
    position: pygame.math.Vector2 = pygame.math.Vector2(0.0, 0.0)
    rotate: int = 0
    velocity: pygame.math.Vector2 = pygame.math.Vector2(0.0, 0.0)

