import sys

from pyglet.window import key

from . import ecs
from .common import get_ship_entity
from .coordinates import screen_to_world
from .ecs import *
from .events import PlacementSelectionEvent, PlaceEvent
from .settings import MOUSE_TURNING
from .vector import V2


class EventSystem(System):

    def setup(self):
        self.subscribe('Key')
        self.subscribe('MouseMotion')
        self.subscribe('MouseClick')
        self.subscribe('MouseScroll')
        self.subscribe('Quit')

    def handle_event(self, event):
        if event.kind == 'Quit':
            sys.exit(0)

        if (event.kind == 'MouseMotion'):
            window_entity = list(Entity.with_component("window"))[0]
            window = window_entity['window']
            camera = window.camera_position
            width, height = window.window.width, window.window.height
            x, y = screen_to_world(
                event.x, event.y,
                width, height,
                camera.x, camera.y,
                window.camera_zoom
            )
            mouse_position = V2(x, y)
            entity = get_ship_entity()
            ship_physics = entity['physics']
            ship_position = ship_physics.position

            if MOUSE_TURNING:
                ship_physics.rotation = (mouse_position - ship_physics.position).degrees - 90

        if (event.kind == 'Key' and event.key_symbol in (key.W, key.A, key.S, key.D, key.LSHIFT, key.F, key.R)):
            inputs = Entity.with_component("input")
            for i in inputs:
                ic = i['input']
                if event.key_symbol == key.W:
                    ic.w = event.pressed
                elif event.key_symbol == key.A:
                    ic.a = event.pressed
                elif event.key_symbol == key.S:
                    ic.s = event.pressed
                elif event.key_symbol == key.D:
                    ic.d = event.pressed
                elif event.key_symbol == key.LSHIFT:
                    ic.boost = event.pressed
                elif event.key_symbol == key.F and event.pressed:
                    ic.mapping = not ic.mapping
                    if ic.mapping:
                        System.inject(Event(kind='StartMapping'))
                    else:
                        System.inject(Event(kind='StopMapping'))
                elif event.key_symbol == key.R:
                    System.inject(Event(kind='Respawn'))

        if (event.kind == 'MouseClick'):
            window_entity = list(Entity.with_component("window"))[0]
            window = window_entity['window']
            camera = window.camera_position
            width, height = window.window.width, window.window.height
            x, y = screen_to_world(
                event.x, event.y,
                width, height,
                camera.x, camera.y,
                window.camera_zoom
            )
            mouse_position = V2(x, y)
            inputs = Entity.with_component("input")
            for i in inputs:
                ic = i['input']
            if event.button == 2 and event.pressed:
                ic.placement = not ic.placement
                if ic.placement:
                    System.inject(Event(kind='StartPlacements'))
                else:
                    System.inject(Event(kind='StopPlacements'))
            if event.button == 1 and event.pressed:
                map_entities = Entity.with_component("map")
                for map_entity in map_entities:
                    if map_entity['map'].is_active:
                        System.inject(
                            PlaceEvent(
                                kind='Place',
                                position=mouse_position,
                                map_entity_id=map_entity.entity_id,
                            )
                        )

        if (event.kind == 'MouseScroll'):
            window_entity = list(Entity.with_component("window"))[0]
            window = window_entity['window']
            if event.scroll_y > 0:
                window.camera_zoom /= 1.1
                System.inject(PlacementSelectionEvent(kind='PlacementSelection', direction='up'))
            else:
                window.camera_zoom *= 1.1
                System.inject(PlacementSelectionEvent(kind='PlacementSelection', direction='down'))

