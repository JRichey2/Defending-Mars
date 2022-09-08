import sys
from pyglet.window import key

from . import ecs
from .settings import MOUSE_TURNING
from .vector import V2
from .events import PlacementSelectionEvent
from .coordinates import screen_to_world

class PlaceEvent(ecs.Event):
    position = ecs.field(type=V2, mandatory=True)


class EventSystem(ecs.System):

    def setup(self):
        self.subscribe('Key')
        self.subscribe('MouseMotion')
        self.subscribe('MouseClick')
        self.subscribe('MouseScroll')
        self.subscribe('Quit')

    def update(self):
        '''Convert inputs to ECS messages for other systems'''

        events, self.events = self.events, []

        for event in events:

            if event.kind == 'Quit':
                sys.exit(0)

            if (event.kind == 'MouseMotion'):
                window_entity = list(ecs.Entity.with_component("window"))[0]
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
                ship_position = ecs.Entity.with_component("input")[0]["physics"].position
                # print(mouse_position, ship_position)
                player = list(ecs.Entity.with_component("input"))[0]
                physics = player['physics']
                if MOUSE_TURNING:
                    physics.rotation = (mouse_position - physics.position).degrees - 90

            if (event.kind == 'Key' and event.key_symbol in (key.W, key.A, key.S, key.D, key.LSHIFT, key.F, key.R)):
                inputs = ecs.Entity.with_component("input")
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
                            ecs.System.inject(ecs.Event(kind='StartMapping'))
                        else:
                            ecs.System.inject(ecs.Event(kind='StopMapping'))
                    elif event.key_symbol == key.R:
                        ecs.System.inject(ecs.Event(kind='Respawn'))

            if (event.kind == 'MouseClick'):
                window_entity = list(ecs.Entity.with_component("window"))[0]
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
                inputs = ecs.Entity.with_component("input")
                for i in inputs:
                    ic = i['input']
                if event.button == 2 and event.pressed:
                    ic.placement = not ic.placement
                    if ic.placement:
                        ecs.System.inject(ecs.Event(kind='StartPlacements'))
                    else:
                        ecs.System.inject(ecs.Event(kind='StopPlacements'))
                if event.button == 1 and event.pressed:
                    ecs.System.inject(PlaceEvent(kind='Place', position=mouse_position))

            if (event.kind == 'MouseScroll'):
                window_entity = list(ecs.Entity.with_component("window"))[0]
                window = window_entity['window']
                if event.scroll_y > 0:
                    window.camera_zoom /= 1.1
                    ecs.System.inject(PlacementSelectionEvent(kind='PlacementSelection', direction='up'))
                else:
                    window.camera_zoom *= 1.1
                    ecs.System.inject(PlacementSelectionEvent(kind='PlacementSelection', direction='down'))
