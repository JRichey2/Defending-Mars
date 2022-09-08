from .ecs import Event, field

class MapEvent(Event):
    map_name = field(type=str, mandatory=True)


class PlacementSelectionEvent(Event):
    direction = field(type=str, mandatory=True)