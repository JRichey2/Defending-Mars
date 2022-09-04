from .ecs import Component
from dataclasses import dataclass
from pygame import Surface


@dataclass
class ScreenComponent(Component):
    screen: Surface 
    background: Surface
    component_name: str = "screen"
    x: int = 0
    y: int = 0
    width: int = 900
    height: int = 500

