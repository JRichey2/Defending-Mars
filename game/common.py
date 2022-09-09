from .ecs import Entity


def get_window():
    windows = Entity.with_component("window")
    if len(windows) == 0:
        return None
    else:
        return windows[0]['window']


def get_ship_entity():
    ships = Entity.with_component("ship")
    if len(ships) == 0:
        return None
    else:
        return ships[0]

