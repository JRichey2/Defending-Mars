from . import ecs
from .vector import V2
from random import random

import pyglet


class PhysicsSystem(ecs.System):

    def update(self):
        self.update_player_ship()
        enemies = ecs.Entity.with_component("enemy")
        for enemy in enemies:
            self.update_enemy_ship(enemy)


    def update_enemy_ship(self, ship):
        physics = ship['physics']
        enemy = ship['enemy']
        flight_path = ecs.Entity.find(enemy.flight_path)["flight path"]
        if enemy.path_index >= len(flight_path.path):
            return
        enemy.target =  flight_path.path[-(enemy.path_index + 1)]
        physics.position -= enemy.offset
        distance_to_target = enemy.target - physics.position
        physics.rotation = distance_to_target.degrees - 90
        if distance_to_target.length < enemy.speed:
            physics.postion = enemy.target
            enemy.path_index += 1
        else:
            physics.position += distance_to_target.normalized * enemy.speed
        physics.position += enemy.offset


    def update_player_ship(self):
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
                acceleration += V2.from_degrees_and_length(rotation + 180, 0.4)
            if inputs.s:
                acceleration += V2.from_degrees_and_length(rotation + 270, 0.4)
            if inputs.d:
                acceleration += V2.from_degrees_and_length(rotation, 0.2)

            if acceleration.length > 0:
                #acceleration.normalize()
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

            emitter = entity['emitter']
            if emitter is None:
                continue

            if not emitter.enabled:
                for sprite in emitter.sprites:
                    sprite.delete()
                emitter.sprites = []
                continue

            if acceleration.length > 0:
                emitter.rate = 0.01
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
                    emitter.image,
                    x=physics.position.x + offset.x,
                    y=physics.position.y + offset.y,
                    batch=emitter.batch,
                    blend_src=pyglet.gl.GL_SRC_ALPHA,
                    blend_dest=pyglet.gl.GL_ONE,
                )
                sprite.rotation = -rotation
                emitter.sprites.append(sprite)
                emitter.time_since_last_emission = 0








