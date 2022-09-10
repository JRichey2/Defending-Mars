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
    top: float = None
    right: float = None


@dataclass
class InputComponent:
    component_name: str = "input"
    w: bool = False
    a: bool = False
    s: bool = False
    d: bool = False
    boost: bool = False
    mapping: bool = False
    placement: bool = False


@dataclass
class PhysicsComponent:
    component_name: str = "physics"
    position: V2 = field(default_factory=V2)
    rotation: float = 0.0
    velocity: V2 = field(default_factory=V2)
    acceleration: V2 = field(default_factory=V2)
    acc_constant: float = 0.25
    drag_constant: float = 0.015
    mass: float = 0.0
    static: bool = True


@dataclass
class ShipComponent:
    component_name: str = "ship"
    boost: float = 100.0
    boosting: bool = False
    boost_constant: float = 1.75


@dataclass
class CheckpointComponent:
    component_name: str = "checkpoint"
    next_image_bottom: pyglet.image.AbstractImage = None
    passed_image_bottom: pyglet.image.AbstractImage = None
    next_image_top: pyglet.image.AbstractImage = None
    passed_image_top: pyglet.image.AbstractImage = None
    finish_image_top: pyglet.image.AbstractImage = None
    finish_image_bottom: pyglet.image.AbstractImage = None
    completed: bool = False
    is_next: bool = False
    cp_order: int = 0
    map_entity_id: int = None


@dataclass
class WindowComponent:
    window: pyglet.window.Window
    component_name: str = "window"
    camera_position: V2 = V2(0.0, 0.0)
    camera_zoom: float = 1.5
    background_layers: list = field(default_factory=list)


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
class FlightPathComponent:
    component_name: str = "flight path"
    path: list[V2] = field(default_factory=list)
    flares: list[pyglet.sprite.Sprite] = field(default_factory=list)


@dataclass
class MapComponent:
    component_name: str = "map"

    # Name of the map for easier recording of records
    map_name: str = "default"

    origin: V2 = None

    # Mode - "racing", "mapping", "editing", or "freeplay"
    mode: str = "racing"

    speedometer_id: int = None

    # Whether or not the entity with this component is the active map
    is_active: bool = True

    ## RECORDING Section ##
    # Used to capture the flight path data as we're recording it
    flight_path: list[dict] = None

    ## EDITING Section ##
    # Used to capture objects during mapping
    map_objects: list[dict] = None

    # Edit selection entity ID
    edit_selection_id: int = None

    edit_selection_index: int = 0

    ## RACING Section ##
    # countdown label entity id
    race_countdown_id: int = None

    # Covers our start time for the race
    race_start_time: float = None

    # Covers our end time for the race
    race_end_time: float = None

    # Stores the flight path/racing line during a race
    racing_line: list[dict] = field(default_factory=list)

    # Stores the personal best racing line
    pb_racing_line: list[dict] = field(default_factory=list)

    # Stores the personal best ghost entity ID
    pb_ghost_entity_id: int = None

    # Stores the personal best racing line entity ID
    pb_line_entity_id: int = None


@dataclass
class CountdownComponent:
    component_name: str = "countdown"

    # Used to select what the countdown is for
    purpose: str = None

    # Time the countdown started
    started_at: float = None

    # Duration of the countdown
    duration: float = None

    # Used to determine if countdown has completed
    completed: bool = False

    # used to capture when we last looked at this value
    last_evaluated: float = None


@dataclass
class CollisionComponent:
    component_name = "collision"
    collider_shape: str = "circle"
    circle_radius: float = 0.0


@dataclass
class MenuComponent:
    component_name: str = "menu"
    menu_name: str = ""
    option_labels: list = field(default_factory=list)
    option_callbacks: dict = field(default_factory=dict)
    selected_option: int = 0
    displayed: bool = False


@dataclass
class AudioComponent:
    component_name: str = "audio"
    fx_volume: float = 0.5
    fx_loops: list[tuple] = field(default_factory=list)

