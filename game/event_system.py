import sys
from pyglet.window import key

from . import ecs


class EventSystem(ecs.System):

    def update(self):
        '''Convert inputs to ECS messages for other systems'''

        events, self.events = self.events, []

        for event in events:

            if event.kind == 'Quit':
                sys.exit(0)

            if (event.kind == 'Key' and event.key_symbol in (key.W, key.A, key.S, key.D, key.Q, key.E)):
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
                    elif event.key_symbol == key.Q:
                        ic.q = event.pressed
                    elif event.key_symbol == key.E:
                        ic.e = event.pressed
                    #print(i, ic)
