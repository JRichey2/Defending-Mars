import pyglet

from .ecs import Entity
from .components import (
    GameVisualComponent,
    Visual,
    PhysicsComponent,
)


def get_inputs():
    inputs = Entity.with_component("input")
    if len(inputs) == 0:
        return None
    else:
        return inputs[0]["input"]


def get_window():
    windows = Entity.with_component("window")
    if len(windows) == 0:
        return None
    else:
        return windows[0]["window"]


def get_ship_entity():
    ships = Entity.with_component("ship")
    if len(ships) == 0:
        return None
    else:
        return ships[0]


def get_active_map_entity():
    map_entities = Entity.with_component("map")
    for map_entity in map_entities:
        if map_entity["map"].is_active:
            return map_entity
    return None


def create_sprite(position, rotation, image, scale=1.0, subpixel=True, z_sort=0.0):
    entity = Entity()
    entity.attach(PhysicsComponent(position=position, rotation=rotation))
    sprite = pyglet.sprite.Sprite(image, x=position.x, y=position.y, subpixel=subpixel)
    sprite.scale = scale
    sprite.rotation = rotation
    entity.attach(
        GameVisualComponent(
            visuals=[Visual(kind="sprite", z_sort=z_sort, value=sprite)]
        )
    )
    return entity


def map_is_active():
    map_entity = get_active_map_entity()
    return bool(map_entity)

