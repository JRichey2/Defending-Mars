from . import ecs

class PhysicsSystem(ecs.System):

    NAME = 'Physics System'

    def update(self):
        entities = ecs.Entity.with_component("input")
        for entity in entities:
            ic = entity['input']
            position = entity['position']
            if position is None:
                continue
            velocity = 5
            position.y -= velocity if ic.w else 0
            position.x -= velocity if ic.a else 0
            position.y += velocity if ic.s else 0
            position.x += velocity if ic.d else 0

