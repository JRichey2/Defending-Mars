from .ecs import Event, field
from .vector import V2


class PlaceEvent(Event):
    position = field(type=V2, mandatory=True)
    map_entity_id = field(type=int)


class MapEvent(Event):
    map_name = field(type=str, mandatory=True)
    map_entity_id = field(type=int)


class PlacementSelectionEvent(Event):
    direction = field(type=str, mandatory=True)


class CountdownEvent(Event):
    countdown_index = field(type=int, mandatory=True)


class KeyEvent(Event):
    key_symbol = field(mandatory=True)
    pressed = field(type=bool, mandatory=True)


class MouseMotionEvent(Event):
    x = field(mandatory=True)
    y = field(mandatory=True)
    dx = field(mandatory=True)
    dy = field(mandatory=True)


class MouseButtonEvent(Event):
    x = field(mandatory=True)
    y = field(mandatory=True)
    button = field(mandatory=True)
    pressed = field(type=bool, mandatory=True)


class MouseScrollEvent(Event):
    x = field(mandatory=True)
    y = field(mandatory=True)
    scroll_x = field(mandatory=True)
    scroll_y = field(mandatory=True)
