from .ecs import Event, field

class MapEvent(Event):
    map_name = field(type=str, mandatory=True)


class PlacementSelectionEvent(Event):
    direction = field(type=str, mandatory=True)


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
