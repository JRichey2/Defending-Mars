from . import ecs
from .vector import V2


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
                acceleration += V2.from_degrees_and_length(position.rotate + 90, 1.0)
            if ic.a:
                acceleration += V2.from_degrees_and_length(position.rotate + 180, 1.0)
            if ic.s:
                acceleration += V2.from_degrees_and_length(position.rotate + 270, 1.0)
            if ic.d:
                acceleration += V2.from_degrees_and_length(position.rotate, 1.0)

            if acceleration.length > 0:
                acceleration.normalize()
                acceleration *= 0.3

            position.velocity *= 0.97
            position.velocity += acceleration
            position.position += position.velocity

            screen = list(ecs.Entity.with_component("screen"))[0]
            sc = screen['screen']
            sc.camera_position.x = position.position.x - 1280 / 2
            sc.camera_position.y = position.position.y - 720 / 2

            # creating another velocity variable in case these need to be a little different
            rotate_velocity = 2.0
            position.rotate -= rotate_velocity if ic.e else 0
            position.rotate += rotate_velocity if ic.q else 0

