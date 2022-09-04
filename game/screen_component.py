from .ecs import Component
from dataclasses import dataclass
from pygame import Surface

@dataclass
class ScreenComponent(Component):
    screen: Surface 
    background: Surface
    component_name: str = "Screen Component"