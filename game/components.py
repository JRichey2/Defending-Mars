from dataclasses import dataclass, field

import pyglet

from . import ecs
from .vector import V2


@dataclass
class InputComponent:
    component_name: str = "input"
    w: bool = False
    a: bool = False
    s: bool = False
    d: bool = False
    boost: bool = False


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

class SpriteCheckpointComponent(pyglet.sprite.Sprite):
    component_name = "checkpoint"
    visible: bool 

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
class EmitterBoostComponent(EmitterComponent):
    boost_image: pyglet.image.AbstractImage = None


@dataclass
class FlightPathComponent:
    component_name = "flight path"
    vertices: pyglet.graphics.vertexdomain.VertexList
    points: pyglet.graphics.vertexdomain.VertexList
    path: list[V2] = field(default_factory=list)


@dataclass
class EnemyComponent(pyglet.sprite.Sprite):
    component_name = "enemy"
    flight_path: str
    target: V2 = V2(0.0, 0.0)
    path_index: int = 0
    speed: float = 0.5
    offset: V2 = V2(0.0, 0.0)


@dataclass
class MassComponent:
    component_name = "mass"
    mass: float


class BoostComponent:

    component_name = "boost"

    def __init__(self):
        window_entity = list(ecs.Entity.with_component("window"))[0]
        window = window_entity['window'].window
        self.boost = 100
        self.ui_base = pyglet.sprite.Sprite(
            window.assets['boost_ui_base'],
            blend_src=pyglet.gl.GL_SRC_ALPHA,
            blend_dest=pyglet.gl.GL_ONE,
        )
        self.ticks = [
            pyglet.sprite.Sprite(
                window.assets['boost_tick_red'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
            pyglet.sprite.Sprite(
                window.assets['boost_tick_yellow'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
            pyglet.sprite.Sprite(
                window.assets['boost_tick_yellow'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
            pyglet.sprite.Sprite(
                window.assets['boost_tick_yellow'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
            pyglet.sprite.Sprite(
                window.assets['boost_tick_yellow'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
            pyglet.sprite.Sprite(
                window.assets['boost_tick_blue'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
            pyglet.sprite.Sprite(
                window.assets['boost_tick_blue'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
            pyglet.sprite.Sprite(
                window.assets['boost_tick_blue'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
            pyglet.sprite.Sprite(
                window.assets['boost_tick_blue'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
            pyglet.sprite.Sprite(
                window.assets['boost_tick_blue'],
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            ),
        ]


