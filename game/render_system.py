import os
import math

import pyglet

from . import ecs
from .ecs import *
from .common import get_ship_entity
from .coordinates import world_to_screen
from .vector import V2


class RenderSystem(System):

    def setup(self):
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glHint(pyglet.gl.GL_LINE_SMOOTH_HINT, pyglet.gl.GL_NICEST)

    def render_bg(self, window):
        width, height = window.window.width, window.window.height
        camera = window.camera_position
        layer_paralax = [10, 8, 2]
        for paralax, sprite in zip(layer_paralax, window.background_layers):

            sl = int(camera.x // paralax) - width // 2
            sr = int(camera.x // paralax + width) - width // 2
            st = int(camera.y // paralax + height) - height // 2
            sb = int(camera.y // paralax) - height // 2

            ixl = int(sl // sprite.width)
            ixr = int(sr // sprite.width)
            ixt = int(st // sprite.height)
            ixb = int(sb // sprite.height)

            paralax_offset_x = width // 2 - camera.x // paralax
            paralax_offset_y = height // 2 - camera.y // paralax

            for tile_index_x in range(ixl, ixr + 1):
                for tile_index_y in range(ixb, ixt + 1):
                    sprite.x = paralax_offset_x + tile_index_x * sprite.width
                    sprite.y = paralax_offset_y + tile_index_y * sprite.height
                    sprite.draw()

    def camera_offset(self, window):
        camera = window.camera_position
        width, height = window.window.width, window.window.height

        zoom = window.camera_zoom
        th = height / 2 - height * zoom / 2
        tw = width / 2 - width * zoom / 2
        l = camera.x + tw - width / 2
        t = camera.y + th - height / 2
        r = camera.x + (width * zoom) + tw - width / 2
        b = camera.y + (height * zoom) + th - height / 2

        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(l, r, t, b, -1.0, 1.0)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(0.375, 0.375, 0.0)

    def reset_camera(self, window):
        width, height = window.window.width, window.window.height
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(0, width, 0, height, -1.0, 1.0)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()

    def draw_flight_path(self, window, entity, visual):
        visual.value.points.draw(pyglet.gl.GL_LINE_STRIP)

    def draw_emitter(self, window, entity, visual):
        visual.value.batch.draw()

    def draw_sprite(self, window, entity, visual):
        physics = entity['physics']
        sprite = visual.value
        if physics is not None:
            sprite.x = physics.position.x
            sprite.y = physics.position.y
            sprite.rotation = float(-physics.rotation)
        sprite.draw()

    def draw_label(self, window, entity, visual):
        # countdown_list = ['Get Ready!', '3', '2', '1', 'GO']
        # if visual.value.text in countdown_list:
        ui_vis = entity['ui visual']
        if ui_vis.right is not None:
            visual.value.x = window.window.width * ui_vis.right
        if ui_vis.top is not None:
            visual.value.y = window.window.height * ui_vis.top
        visual.value.draw()

    def draw_boost_meter(self, window, entity, visual):
        ship = entity["ship"]
        base = visual.value['base']
        ticks = visual.value['ticks']
        base.opacity = 127
        base.x = window.window.width - 160
        base.y = 50
        base.draw()

        for i, tick in enumerate(ticks):
            lb = i * 20
            ub = i * 20 + 20
            ab = min(max(ship.boost, lb),ub)
            alpha = (ab - lb) / 20
            tick.opacity = int(127 * alpha)
            tick.x = window.window.width - 56
            tick.y = 34 + (i + 1) * 34
            tick.draw()


    def calculate_line_intersection(self, p1, p2, normal, line_position, vertical=True):
        v = p2 - p1
        n = normal
        a1 = n * (v.dot_product(n))
        if vertical:
            h0 = line_position - p1.x
            h1 = p2.x - p1.x
        else:
            h0 = line_position - p1.y
            h1 = p2.y - p1.y
        r = h0 / h1
        a0 = a1 * r
        min_x = min(p1.x, p2.x)
        max_x = max(p1.x, p2.x)
        min_y = min(p1.y, p2.y)
        max_y = max(p1.y, p2.y)
        if vertical:
            a_y = a0.y + p1.y
            a_x = h0 + p1.x
        else:
            a_x = a0.x + p1.x
            a_y = h0 + p1.y
        if min_x <= a_x <= max_x and min_y <= a_y <= max_y:
            return True, V2(a_x, a_y)
        else:
            return False, None

    def draw_checkpoint_arrow(self, window, entity, visual):
        width, height = window.window.width, window.window.height
        camera = window.camera_position
        cp = entity['checkpoint']
        physics = entity['physics']
        arrow = entity['ui visual'].visuals[0].value

        zoom = window.camera_zoom

        if cp.is_next:
            arrow_x, arrow_y = world_to_screen(
                physics.position.x, physics.position.y,
                width, height,
                camera.x, camera.y,
                zoom
            )

            half_sprite_x = 128 / zoom
            half_sprite_y = 128 / zoom

            # Check if original sprite was off the screen, and draw if so
            if (     arrow_y < -half_sprite_y
                  or arrow_y >  half_sprite_y + height
                  or arrow_x < -half_sprite_x
                  or arrow_x >  half_sprite_x + width):
                # Clamp arrow to on the screen edge

                entity = get_ship_entity()
                ship_physics = entity["physics"]

                ship_x, ship_y = world_to_screen(
                    ship_physics.position.x, ship_physics.position.y,
                    width, height,
                    camera.x, camera.y,
                    zoom
                )

                arrow_point = V2(arrow_x, arrow_y)
                ship_point = V2(ship_x, ship_y)

                intersections = []

                intersections.append(self.calculate_line_intersection(
                    ship_point,
                    arrow_point,
                    V2(-1.0, 0.0),
                    height,
                    vertical=False
                ))

                intersections.append(self.calculate_line_intersection(
                    ship_point,
                    arrow_point,
                    V2(1.0, 0.0),
                    0,
                    vertical=False
                ))

                intersections.append(self.calculate_line_intersection(
                    ship_point,
                    arrow_point,
                    V2(0.0, -1.0),
                    width,
                    vertical=True
                ))

                intersections.append(self.calculate_line_intersection(
                    ship_point,
                    arrow_point,
                    V2(0.0, 1.0),
                    0,
                    vertical=True
                ))

                intersections = [(i, p) for i, p in intersections if p is not None]

                e = 1.0
                intersections = [
                    p for i, p in intersections
                    if i and (0 - e <= p.x <= width + e) and (0 - e <= p.y <= height + e)
                ]

                if len(intersections) > 0:
                    v = physics.position - ship_physics.position
                    arrow.rotation = -(v.degrees)
                    arrow.x = intersections[0].x
                    arrow.y = intersections[0].y
                    arrow.draw()

    def update(self):
        window_entity = Entity.with_component("window")[0]
        window = window_entity['window']

        self.render_bg(window)

        self.camera_offset(window)

        entities = Entity.with_component("game visual")
        visuals = []
        for entity in entities:
            for visual in entity['game visual'].visuals:
                visuals.append((entity, visual))

        for entity, visual in sorted(visuals, key=lambda x: x[1].z_sort):
            if visual.kind == 'emitter':
                self.draw_emitter(window, entity, visual)
            elif visual.kind == 'flight path':
                self.draw_flight_path(window, entity, visual)
            elif visual.kind == 'sprite':
                self.draw_sprite(window, entity, visual)

        self.reset_camera(window)

        entities = Entity.with_component("ui visual")
        visuals = []
        for entity in entities:
            for visual in entity['ui visual'].visuals:
                visuals.append((entity, visual))

        for entity, visual in sorted(visuals, key=lambda x: x[1].z_sort):
            if visual.kind == 'checkpoint arrow':
                self.draw_checkpoint_arrow(window, entity, visual)
            elif visual.kind == 'boost':
                self.draw_boost_meter(window, entity, visual)
            elif visual.kind == 'label':
                self.draw_label(window, entity, visual)

