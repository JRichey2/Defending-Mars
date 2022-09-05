from . import ecs
from .vector import V2


class PhysicsSystem(ecs.System):

    def update(self):
        entities = ecs.Entity.with_component("input")
        for entity in entities:
            inputs = entity['input']
            physics = entity['physics']
            print(entity)
            if physics is None:
                continue

            rotation = physics.rotation
            acceleration = V2(0.0, 0.0)

            if inputs.w:
                acceleration += V2.from_degrees_and_length(rotation + 90, 1.0)
            if inputs.a:
                acceleration += V2.from_degrees_and_length(rotation + 180, 1.0)
            if inputs.s:
                acceleration += V2.from_degrees_and_length(rotation + 270, 1.0)
            if inputs.d:
                acceleration += V2.from_degrees_and_length(rotation, 1.0)

            if acceleration.length > 0:
                acceleration.normalize()
                acceleration *= 0.3

            physics.velocity *= 0.97
            physics.velocity += acceleration
            physics.position += physics.velocity

            screen = list(ecs.Entity.with_component("screen"))[0]
            sc = screen['screen']
            sc.camera_position.x = physics.position.x - 1280 / 2
            sc.camera_position.y = physics.position.y - 720 / 2

            physics.rotation -= 2.0 if inputs.e else 0
            physics.rotation += 2.0 if inputs.q else 0

