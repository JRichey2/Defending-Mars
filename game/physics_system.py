from . import ecs

class PhysicsSystem(ecs.System):
    
    NAME = 'Physics System'

    def update(self):
        entities = ecs.Entity.with_component("Input Component")
        for entity in entities:
            position = [c for c in entity.components if c.component_name == 'Position Component']
            if len(position) == 0:
                continue
            position = position[0]
            ic = [c for c in entity.components if c.component_name == 'Input Component'][0]
            velocity = 5
            position.y -= velocity if ic.w else 0
            position.x -= velocity if ic.a else 0
            position.y += velocity if ic.s else 0
            position.x += velocity if ic.d else 0