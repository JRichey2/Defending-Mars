from . import ecs


# This is just an example system that echos back events

class EchoSystem(ecs.System):

    NAME = 'Echo System'

    def update(self):
        events, self.events = self.events, []
        entities = ecs.Entity.with_component("Echo Component")
        if len(events) > 0:
            print('events', events)
            print('entities', entities)

