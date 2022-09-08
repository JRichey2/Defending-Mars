from dataclasses import dataclass, field

import pyglet

from . import ecs
from .vector import V2


@dataclass
class Visual:
    kind: str
    z_sort: float
    value: object


@dataclass
class GameVisualComponent:
    component_name: str = "game visual"
    visuals: list[Visual] = field(default_factory=list)


@dataclass
class UIVisualComponent:
    component_name: str = "ui visual"
    visuals: list[Visual] = field(default_factory=list)


@dataclass
class InputComponent:
    component_name: str = "input"
    w: bool = False
    a: bool = False
    s: bool = False
    d: bool = False
    boost: bool = False
    mapping: bool = False


@dataclass
class PhysicsComponent:
    component_name: str = "physics"
    position: V2 = V2(0.0, 0.0)
    rotation: int = 0
    velocity: V2 = V2(0.0, 0.0)


class SpriteComponent(pyglet.sprite.Sprite):
    component_name = "sprite"


@dataclass
class SpriteCheckpointComponent:
    component_name = "checkpoint"
    next_image_bottom: pyglet.image.AbstractImage
    passed_image_bottom: pyglet.image.AbstractImage
    next_image_top: pyglet.image.AbstractImage
    passed_image_top: pyglet.image.AbstractImage
    completed: bool = False
    is_next: bool = False
    cp_order: int = 0


@dataclass
class WindowComponent:
    window: pyglet.window.Window
    component_name: str = "window"
    camera_position: V2 = V2(0.0, 0.0)
    background_layers: list[SpriteComponent] = field(default_factory=list)


@dataclass
class Emitter:
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
class EmitterBoost(Emitter):
    boost_image: pyglet.image.AbstractImage = None


@dataclass
class FlightPath:
    points: pyglet.graphics.vertexdomain.VertexList
    path: list[V2] = field(default_factory=list)


@dataclass
class MapComponent:
    map_name: str
    component_name: str = "map"


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


@dataclass
class CollisionComponent:
    component_name = "collision"
    collider_shape: str = "circle"
    circle_radius: float = 0.0


@dataclass
class BoostComponent:
    component_name = "boost"
    boost: float = 100.0


