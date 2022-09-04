from . import ecs
from pygame.math import Vector2 as V2

class PhysicsSystem(ecs.System):

    def update(self):
        entities = ecs.Entity.with_component("input")
        for entity in entities:
            ic = entity['input']
            position = entity['position']
            if position is None:
                continue
            acceleration = V2(0.0, 0.0)

            if ic.w:
                acceleration += V2(0.0, -1.0).rotate(-position.rotate)
            if ic.a:
                acceleration += V2(-1.0, 0.0).rotate(-position.rotate)
            if ic.s:
                acceleration += V2(0.0, 1.0).rotate(-position.rotate)
            if ic.d:
                acceleration += V2(1.0, 0.0).rotate(-position.rotate)

            if acceleration.length() > 0:
                acceleration = acceleration.normalize()
                acceleration = acceleration * 0.3

            position.velocity *= 0.97

            position.velocity += acceleration
            
            position.position += position.velocity

            screen = list(ecs.Entity.with_component("screen"))[0]
            sc = screen['screen']
            sc.x = int(position.position.x - sc.width // 2)
            sc.y = int(position.position.y - sc.height // 2)

            # creating another velocity variable in case these need to be a little different
            rotate_velocity = 2.0
            position.rotate -= rotate_velocity if ic.e else 0
            position.rotate += rotate_velocity if ic.q else 0

