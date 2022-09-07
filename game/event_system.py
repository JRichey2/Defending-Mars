import sys
from pyglet.window import key

from . import ecs
from .vector import V2


class EventSystem(ecs.System):

    def setup(self):
        self.subscribe('Key')
        self.subscribe('MouseMotion')
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
                ox = width // 2 - camera.x
                oy = height // 2 - camera.y
                mouse_position = V2(event.x - ox, event.y - oy)
                player = list(ecs.Entity.with_component("input"))[0]
                physics = player['physics']
                physics.rotation = (mouse_position - physics.position).degrees - 90

            if (event.kind == 'Key' and event.key_symbol in (key.W, key.A, key.S, key.D, key.LSHIFT, key.F)):
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

