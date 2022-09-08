from . import ecs
from .ecs import Event
from . import settings
from .settings import MOUSE_TURNING, CAMERA_SPRING
from .vector import V2
from random import random

import pyglet


class PhysicsSystem(ecs.System):

    def setup(self):
        self.subscribe('CenterCamera')
        self.subscribe('Respawn')

    def update(self):
        events, self.events = self.events, []

        for event in events:

            if event.kind == 'CenterCamera':
                window_entity = ecs.Entity.with_component("window")[0]
                ship_entity = ecs.Entity.with_component("input")[0]
                window_entity['window'].camera_position = ship_entity['physics'].position.copy

            elif event.kind == 'Respawn':
                ship_entity = ecs.Entity.with_component("input")[0]
                checkpoints = ecs.Entity.with_component("checkpoint")
                completed_checkpoint = None
                for entity in checkpoints:
                    checkpoint = entity['checkpoint']
                    if checkpoint.completed:
                        completed_checkpoint = entity
                if completed_checkpoint:
                    physics = completed_checkpoint['physics']
                    pos = physics.position.copy
                    ship_entity['physics'].position = pos
                    ship_entity['physics'].velocity = V2(0, 0)

        self.update_player_ship()
        enemies = ecs.Entity.with_component("enemy")
        for enemy in enemies:
            self.update_enemy_ship(enemy)
        self.update_flares()

    def update_flares(self):
        dt = ecs.DELTA_TIME
        time_factor = dt / 0.01667
        ship = ecs.Entity.with_component("input")[0]
        ship_position = ship['physics'].position

        for entity in ecs.Entity.with_component("game visual"):
            emitters = [
                v.value for v in entity['game visual'].visuals
                if v.kind == 'emitter'
            ]

            if entity.entity_id == ship.entity_id:
                # Skip the ship
                continue

            physics = entity['physics']
            if physics is None:
                continue

            for emitter in emitters:

                distance = (ship_position - physics.position).length
                if distance < 750:
                    emitter.enabled = True
                    emitter.rate = distance / 750
                else:
                    emitter.enabled = False

                if not emitter.enabled:
                    for sprite in emitter.sprites:
                        sprite.delete()
                    emitter.sprites = []
                    continue

                for sprite in emitter.sprites:
                    sprite.opacity *= 1 - (0.03 * time_factor)

                to_be_deleted = [s for s in emitter.sprites if s.opacity < 0.01]
                emitter.sprites = [s for s in emitter.sprites if s.opacity >= 0.01]
                for sprite in to_be_deleted:
                    sprite.delete()

                emitter.time_since_last_emission += dt
                if emitter.time_since_last_emission > emitter.rate:
                    sprite = pyglet.sprite.Sprite(
                        emitter.image,
                        x=physics.position.x,
                        y=physics.position.y,
                        batch=emitter.batch,
                        blend_src=pyglet.gl.GL_SRC_ALPHA,
                        blend_dest=pyglet.gl.GL_ONE,
                    )
                    emitter.sprites.append(sprite)
                    emitter.time_since_last_emission = 0


    def update_player_ship(self):
        entities = ecs.Entity.with_component("mass")

        if settings.GRAVITY:
            GRAV_CONSTANT = 150.0
        else:
            GRAV_CONSTANT = 0.0
        if settings.ACCELERATION:
            ACC_CONSTANT = 0.25
        else:
            ACC_CONSTANT = 0.0
        BOOST_CONSTANT = 1.75
        DRAG_CONSTANT = 0.015
        MAX_GRAV_ACC = 0.24

        dt = ecs.DELTA_TIME
        time_factor = dt / 0.01667

        mass_points = []
        for entity in entities:
            physics = entity['physics']
            if physics is None:
                continue
            mass = entity['mass']
            mass_points.append((physics.position, mass.mass))

        entities = ecs.Entity.with_component("input")
        for entity in entities:
            inputs = entity['input']
            physics = entity['physics']
            if physics is None:
                continue

            rotation = physics.rotation
            acceleration = V2(0.0, 0.0)

            if inputs.a:
                if not settings.MOUSE_TURNING:
                    rotation += 3.0 * time_factor
                else:
                    acceleration += V2.from_degrees_and_length(rotation + 180, 0.4)
            if inputs.d:
                if not settings.MOUSE_TURNING:
                    rotation -= 3.0 * time_factor
                else:
                    acceleration += V2.from_degrees_and_length(rotation, 0.4)

            if inputs.w or inputs.boost:
                acceleration += V2.from_degrees_and_length(rotation + 90, 1.0)
            if inputs.s:
                acceleration += V2.from_degrees_and_length(rotation + 270, 0.4)


            if not settings.MOUSE_TURNING:
                physics.rotation = rotation


            if acceleration.length > 0:
                #acceleration.normalize()
                acceleration *= ACC_CONSTANT
            boost = entity['boost']
            if inputs.boost and settings.BOOST:
                if boost.boost > 0:
                    acceleration *= BOOST_CONSTANT
                    boost.boost -= 0.5 * time_factor
                    boosting = True
                else:
                    boosting = False
            else:
                if boost.boost < 100:
                    boost.boost += 0.1 * time_factor
                boosting = False


            grav_acc = V2(0,0)
            for mass_point, mass in mass_points:
                acc_vector = mass_point - physics.position
                if acc_vector.length_squared > 0:
                    acc_magnitude = GRAV_CONSTANT * mass / acc_vector.length_squared
                    acc_magnitude = min(acc_magnitude, MAX_GRAV_ACC)
                    grav_acc += acc_vector.normalized * acc_magnitude


            physics.velocity *= 1 - (DRAG_CONSTANT * time_factor)
            physics.velocity += acceleration * time_factor
            physics.velocity += grav_acc * time_factor
            physics.position += physics.velocity * time_factor

            window_entity = list(ecs.Entity.with_component("window"))[0]
            window = window_entity['window']
            width, height = window.window.width, window.window.height
            if settings.CAMERA_SPRING:
                target_camera_position = (
                    physics.position
                        + physics.velocity
                        * 20 * (min(width, height) / 720)
                )
                target_camera_vector = target_camera_position - window.camera_position
                if target_camera_vector.length != 0:
                    camera_adjustment = (
                            target_camera_vector.normalized
                            * min(target_camera_vector.length * 0.05, 60 * time_factor)
                    )

                    window.camera_position = window.camera_position + camera_adjustment
            else:
                window.camera_position = physics.position.copy

            game_visual = entity['game visual']
            if game_visual is None:
                continue

            emitter = None
            for visual in game_visual.visuals:
                if visual.kind == 'emitter':
                    emitter = visual.value
                    break

            if emitter is None:
                continue

            if not emitter.enabled:
                for sprite in emitter.sprites:
                    sprite.delete()
                emitter.sprites = []
                continue

            if acceleration.length > 0 and boosting:
                emitter.rate = 0.005
            elif acceleration.length > 0:
                emitter.rate = 0.015
            else:
                emitter.rate = 0.03

            for sprite in emitter.sprites:
                sprite.opacity *= 1 - (0.1 * time_factor)

            to_be_deleted = [s for s in emitter.sprites if s.opacity < 0.01]
            emitter.sprites = [s for s in emitter.sprites if s.opacity >= 0.01]
            for sprite in to_be_deleted:
                sprite.delete()

            emitter.time_since_last_emission += dt
            if emitter.time_since_last_emission > emitter.rate:
                offset = V2.from_degrees_and_length(rotation + 270, 16.0)
                sprite = pyglet.sprite.Sprite(
                    emitter.image if not (hasattr(emitter, "boost_image") and boosting) else emitter.boost_image,
                    x=physics.position.x + offset.x,
                    y=physics.position.y + offset.y,
                    batch=emitter.batch,
                    blend_src=pyglet.gl.GL_SRC_ALPHA,
                    blend_dest=pyglet.gl.GL_ONE,
                )
                sprite.rotation = -rotation
                emitter.sprites.append(sprite)
                emitter.time_since_last_emission = 0

            collision = entity['collision']
            if collision is None:
                return
            colliders = ecs.Entity.with_component("collision")
            for collider in colliders:
                # Don't collide with self
                if collider.entity_id == entity.entity_id:
                    continue
                collider_collision = collider['collision']
                collider_physics = collider['physics']
                if collider_physics is None:
                    continue
                separation = physics.position - collider_physics.position
                sep_length = separation.length
                min_length = collision.circle_radius + collider_collision.circle_radius
                if sep_length < min_length:
                    n = separation.normalized
                    v = physics.velocity
                    a = n * (v.dot_product(n))
                    physics.position += separation.normalized * (min_length - sep_length)
                    physics.velocity = (v - (a * 1.3)) * 0.9











