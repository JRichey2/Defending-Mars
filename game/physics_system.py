from random import random

import pyglet

from . import ecs
from . import settings
from .common import *
from .ecs import *
from .settings import MOUSE_TURNING, CAMERA_SPRING
from .vector import V2


class PhysicsSystem(System):

    def setup(self):
        self.subscribe('CenterCamera', self.handle_center_camera)
        self.subscribe('Respawn', self.handle_respawn)

    def handle_center_camera(self, **kwargs):
        window = get_window()
        ship_entity = get_ship_entity()
        ship_physics = ship_entity['physics']
        window.camera_position = ship_physics.position

    def handle_respawn(self, **kwargs):
        ship_entity = get_ship_entity()
        ship_physics = ship_entity['physics']
        checkpoints = Entity.with_component("checkpoint")
        completed_checkpoint = None
        for entity in checkpoints:
            checkpoint = entity['checkpoint']
            if checkpoint.completed:
                completed_checkpoint = entity
        if completed_checkpoint:
            checkpoint_physics = completed_checkpoint['physics']
            ship_physics.position = checkpoint_physics.position
            ship_physics.velocity = V2(0, 0)

    def update(self):
        self.update_ship_controls()
        self.update_all_physics_objects()
        self.update_ship_thrust_emitter()
        self.update_ship_collision()
        self.update_camera_position()
        self.update_flares()

    def update_flares(self):
        dt = ecs.DELTA_TIME
        time_factor = dt / 0.01667
        ship_entity = get_ship_entity()
        ship_position = ship_entity['physics'].position

        for entity in Entity.with_component("game visual"):
            emitters = [
                v.value for v in entity['game visual'].visuals
                if v.kind == 'emitter'
            ]

            if entity.entity_id == ship_entity.entity_id:
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

    def get_all_masses(self):
        mass_points = []
        for entity in Entity.with_component("physics"):
            physics = entity['physics']
            if physics.mass != 0.0:
                mass_points.append((physics.position, physics.mass))
        return mass_points

    def update_all_physics_objects(self):
        dt = ecs.DELTA_TIME
        time_factor = dt / 0.01667

        for entity in Entity.with_component("physics"):
            physics = entity['physics']

            # Don't calculate velocity, position, acceleration,
            # boost, gravity, etc. for static objects
            if physics.static:
                continue

            mass_points = self.get_all_masses()

            gravity = settings.GRAV_CONSTANT if settings.GRAVITY else 0.0
            max_grav_acc = settings.MAX_GRAV_ACC if settings.GRAVITY else 0.0

            grav_acc = V2(0,0)
            for mass_point, mass in mass_points:
                acc_vector = mass_point - physics.position
                if acc_vector.length_squared > 0:
                    acc_magnitude = gravity * mass / acc_vector.length_squared
                    grav_acc += acc_vector.normalized * acc_magnitude

            acc_magnitude = grav_acc.length
            acc_magnitude = min(acc_magnitude, max_grav_acc)
            if grav_acc.length_squared > 0.0:
                grav_acc = grav_acc.normalized * acc_magnitude
                physics.acceleration += grav_acc

            physics.velocity *= 1 - (settings.DRAG_CONSTANT * time_factor)
            physics.velocity += physics.acceleration * time_factor
            physics.position += physics.velocity * time_factor

    def update_ship_controls(self):
        dt = ecs.DELTA_TIME
        time_factor = dt / 0.01667

        inputs = Entity.with_component('input')[0]['input']
        entity = get_ship_entity()
        physics = entity['physics']

        rotation = physics.rotation
        physics.acceleration = V2(0.0, 0.0)

        if inputs.a:
            if not settings.MOUSE_TURNING:
                rotation += 3.0 * time_factor
            else:
                physics.acceleration += V2.from_degrees_and_length(rotation + 180, 0.4)

        if inputs.d:
            if not settings.MOUSE_TURNING:
                rotation -= 3.0 * time_factor
            else:
                physics.acceleration += V2.from_degrees_and_length(rotation, 0.4)

        if inputs.w or inputs.boost:
            physics.acceleration += V2.from_degrees_and_length(rotation + 90, 1.0)

        if inputs.s:
            physics.acceleration += V2.from_degrees_and_length(rotation + 270, 0.4)

        if not settings.MOUSE_TURNING:
            physics.rotation = rotation

        acc_constant = settings.ACC_CONSTANT if settings.ACCELERATION else 0.0
        physics.acceleration *= acc_constant

        ship = entity['ship']

        boost_constant = settings.BOOST_CONSTANT if settings.BOOST else 0.0

        if inputs.boost and settings.BOOST:
            if ship.boost > 0:
                physics.acceleration *= boost_constant
                ship.boost -= 0.5 * time_factor
                ship.boosting = True
            else:
                ship.boosting = False
        else:
            if ship.boost < 100:
                ship.boost += 0.1 * time_factor
            ship.boosting = False


    def update_camera_position(self):
        dt = ecs.DELTA_TIME
        time_factor = dt / 0.01667

        entity = get_ship_entity()
        physics = entity['physics']
        window_entity = list(Entity.with_component("window"))[0]
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
            window.camera_position = physics.position


    def update_ship_thrust_emitter(self):
        dt = ecs.DELTA_TIME
        time_factor = dt / 0.01667

        entity = get_ship_entity()
        ship = entity['ship']
        physics = entity['physics']
        game_visual = entity['game visual']

        emitter = None
        for visual in game_visual.visuals:
            if visual.kind == 'emitter':
                emitter = visual.value
                break

        if emitter is None:
            return

        if not emitter.enabled:
            for sprite in emitter.sprites:
                sprite.delete()
            emitter.sprites = []
            return

        if physics.acceleration.length > 0 and ship.boosting:
            emitter.rate = 0.005
        elif physics.acceleration.length > 0:
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
            offset = V2.from_degrees_and_length(physics.rotation + 270, 16.0)
            sprite = pyglet.sprite.Sprite(
                emitter.image if not (hasattr(emitter, "boost_image") and ship.boosting) else emitter.boost_image,
                x=physics.position.x + offset.x,
                y=physics.position.y + offset.y,
                batch=emitter.batch,
                blend_src=pyglet.gl.GL_SRC_ALPHA,
                blend_dest=pyglet.gl.GL_ONE,
            )
            sprite.rotation = -physics.rotation
            emitter.sprites.append(sprite)
            emitter.time_since_last_emission = 0


    def update_ship_collision(self):
        entity = get_ship_entity()
        physics = entity['physics']

        collision = entity['collision']
        if collision is None:
            return

        colliders = Entity.with_component("collision")
        for collider in colliders:

            if collider.entity_id == entity.entity_id:
                # Don't collide with self
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

