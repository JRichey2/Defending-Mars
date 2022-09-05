from . import ecs
from .vector import V2


class PhysicsSystem(ecs.System):

    def update(self):
        entities = ecs.Entity.with_component("input")
        for entity in entities:
            inputs = entity['input']
            physics = entity['physics']
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


            dt = ecs.DELTA_TIME
            time_factor = dt / 0.01667
            physics.velocity *= 1 - (0.03 * time_factor)
            physics.velocity += acceleration * time_factor
            physics.position += physics.velocity * time_factor

            window_entity = list(ecs.Entity.with_component("window"))[0]
            window = window_entity['window']
            window.camera_position.x = physics.position.x
            window.camera_position.y = physics.position.y

            physics.rotation -= 2.0 if inputs.e else 0
            physics.rotation += 2.0 if inputs.q else 0

