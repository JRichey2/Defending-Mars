from . import ecs
from .vector import V2

import pyglet
import os
import math


class RenderSystem(ecs.System):


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
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glTranslatef(width / 2 - camera.x, height / 2 - camera.y, 0.0)

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

    def draw_boost_meter(self, window, entity, visual):
        boost = entity["boost"]
        base = visual.value['base']
        ticks = visual.value['ticks']
        base.opacity = 127
        boost.blend_src=pyglet.gl.GL_SRC_ALPHA,
        boost.blend_dest=pyglet.gl.GL_ONE,
        base.x = window.window.width - 160
        base.y = 50
        base.draw()

        for i, tick in enumerate(ticks):
            lb = i * 20
            ub = i * 20 + 20
            ab = min(max(boost.boost, lb),ub)
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
        ox = width / 2 - camera.x
        oy = height / 2 - camera.y
        points = [
            (0.0  , 0.0   ),
            (width, 0.0   ),
            (0.0  , height),
            (width, height),
        ]
        vecs = [V2(p[0] - ox, p[1] - oy) for p in points]
        cp = entity['checkpoint']
        physics = entity['physics']
        arrow = entity['ui visual'].visuals[0].value

        if cp.is_next:
            x_ob = physics.position.x + ox
            y_ob = physics.position.y + oy
            half_sprite_x = 128
            half_sprite_y = 128
            half_arrow_x = 64
            half_arrow_y = 64

            # Check if original sprite was off the screen, and draw if so
            if (     y_ob < -half_sprite_y
                  or y_ob >  half_sprite_y + height
                  or x_ob < -half_sprite_x
                  or x_ob >  half_sprite_x + width):
                # Clamp arrow to on the screen edge

                ship = ecs.Entity.with_component("input")[0]
                ship_physics = ship["physics"]

                intersections = []

                intersections.append(self.calculate_line_intersection(
                    ship_physics.position,
                    physics.position,
                    V2(-1.0, 0.0),
                    (height - oy),
                    vertical=False
                ))

                intersections.append(self.calculate_line_intersection(
                    ship_physics.position,
                    physics.position,
                    V2(1.0, 0.0),
                    (0 - oy),
                    vertical=False
                ))

                intersections.append(self.calculate_line_intersection(
                    ship_physics.position,
                    physics.position,
                    V2(0.0, -1.0),
                    (width - ox),
                    vertical=True
                ))

                intersections.append(self.calculate_line_intersection(
                    ship_physics.position,
                    physics.position,
                    V2(0.0, 1.0),
                    (0 - ox),
                    vertical=True
                ))

                intersections = [(i, p + V2(ox, oy)) for i, p in intersections if p is not None]

                intersections = [
                    p for i, p in intersections
                    if i and (0 <= p.x <= width) and (0 <= p.y <= height)
                ]

                if len(intersections) > 0:
                    v = physics.position - ship_physics.position
                    arrow.rotation = -(v.degrees)
                    arrow.x = intersections[0].x
                    arrow.y = intersections[0].y
                    arrow.draw()


    def update(self):
        window_entity = ecs.Entity.with_component("window")[0]
        window = window_entity['window']

        self.render_bg(window)

        self.camera_offset(window)

        entities = ecs.Entity.with_component("game visual")
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

        pyglet.gl.glLoadIdentity()

        entities = ecs.Entity.with_component("ui visual")
        visuals = []
        for entity in entities:
            for visual in entity['ui visual'].visuals:
                visuals.append((entity, visual))

        for entity, visual in sorted(visuals, key=lambda x: x[1].z_sort):
            if visual.kind == 'checkpoint arrow':
                self.draw_checkpoint_arrow(window, entity, visual)
            elif visual.kind == 'boost':
                self.draw_boost_meter(window, entity, visual)

