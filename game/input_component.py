from .ecs import Component
from dataclasses import dataclass

@dataclass
class InputComponent(Component):
    component_name: str = "input"
    w: bool = False 
    a: bool = False 
    s: bool = False 
    d: bool = False 
