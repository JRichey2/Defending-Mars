from dataclasses import dataclass, field

import pyglet

from .vector import V2


@dataclass
class InputComponent:
    component_name: str = "input"
    w: bool = False
    a: bool = False
    s: bool = False
    d: bool = False
    


@dataclass
class PhysicsComponent:
    component_name: str = "physics"
    position: V2 = V2(0.0, 0.0)
    rotation: int = 0
    velocity: V2 = V2(0.0, 0.0)


class SpriteComponent(pyglet.sprite.Sprite):
    component_name = "sprite"

class SpriteComponentLocator(pyglet.sprite.Sprite):
    component_name = "spritelocator"

@dataclass
class WindowComponent:
    window: pyglet.window.Window
    viewport_size: V2
    component_name: str = "window"
    camera_position: V2 = V2(0.0, 0.0)
    background_layers: list[SpriteComponent] = field(default_factory=list)


@dataclass
class EmitterComponent:
    component_name = 'emitter'
    image: pyglet.image.AbstractImage
    # A sprite batch to draw all of the emitted particles
    batch: pyglet.graphics.Batch
    # A list of sprites that have been emitted
    sprites: list[pyglet.sprite.Sprite] = field(default_factory=list)
    # time between each particle
    rate: float = 1.0
    # records last time particle was emitted
    time_since_last_emission: float = 0.0
    # Determines if particles should be emitting currently
    enabled: bool = True


@dataclass
class FlightPathComponent:
    component_name = "flight path"
    vertices: pyglet.graphics.vertexdomain.VertexList
    points: pyglet.graphics.vertexdomain.VertexList

