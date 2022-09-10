import os
import math

import pyglet

from . import ecs
from .settings import settings
from .ecs import *
from .common import *
from .coordinates import *
from .vector import *


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

    def draw_flight_path_line(self, window, entity, visual):
        visual.value.draw(pyglet.gl.GL_LINE_STRIP)

    def draw_emitter(self, window, entity, visual):
        visual.value.batch.draw()

    def draw_sprite_batch(self, window, entity, visual):
        visual.value.draw()

    def draw_tutorial_text(self, window, entity, visual):
        visual.value.x = entity['physics'].position.x
        visual.value.y = entity['physics'].position.y
        visual.value.draw()

    def draw_flare(self, window, entity, visual, ship_entity):
        physics = entity["physics"]
        ship_physics = ship_entity["physics"]
        sprite = visual.value
        distance = (ship_physics.position - physics.position).length
        fade_distance = 700
        if distance > fade_distance:
            return
        sprite.opacity = int((1 - (distance / fade_distance)) * 255)
        sprite.draw()

    def draw_sprite(self, window, entity, visual):
        physics = entity["physics"]
        sprite = visual.value
        if physics is not None:
            sprite.x = physics.position.x
            sprite.y = physics.position.y
            sprite.rotation = float(-physics.rotation)
        sprite.draw()

    def draw_real_time_label(self, window, entity, visual):
        ui_vis = entity["ui visual"]
        value = visual.value
        label = value["label"]
        label.text = value["fn"]()
        if ui_vis.right is not None:
            label.x = window.window.width * ui_vis.right
        if ui_vis.top is not None:
            label.y = window.window.height * ui_vis.top
        label.draw()

    def draw_label(self, window, entity, visual):
        ui_vis = entity["ui visual"]
        if ui_vis.right is not None:
            visual.value.x = window.window.width * ui_vis.right
        if ui_vis.top is not None:
            visual.value.y = window.window.height * ui_vis.top
        visual.value.draw()

    def draw_menu_options(self, window, entity, visual):
        menu = entity["menu"]
        if not menu.displayed:
            return

        ui_vis = entity["ui visual"]
        labels = visual.value

        w, h = window.window.width, window.window.height
        origin_x, origin_y = w * ui_vis.right, h * ui_vis.top

        for i, label in enumerate(labels):
            label.text = menu.option_labels[i]
            label.x = origin_x
            label.y = origin_y - 64 * i
            if i == menu.selected_option:
                label.color = (0, 200, 255, 225)
            else:
                label.color = (255, 255, 255, 160)
            label.draw()

    def draw_menu_sprite(self, window, entity, visual):
        menu = entity["menu"]
        if not menu.displayed:
            return
        ui_vis = entity["ui visual"]
        sprite = visual.value
        w, h = window.window.width, window.window.height
        origin_x, origin_y = w * 0.78, h * ui_vis.top
        sprite.x = origin_x
        sprite.y = origin_y
        sprite.draw()

    def draw_menu_description(self, window, entity, visual):
        menu = entity["menu"]
        if not menu.displayed:
            return
        ui_vis = entity["ui visual"]
        label = visual.value
        w, h = window.window.width, window.window.height
        origin_x, origin_y = w * 0.78, h * ui_vis.top - 150
        label.x = origin_x
        label.y = origin_y
        label.draw()

    def draw_boost_meter(self, window, entity, visual):
        if settings.PHYSICS_FROZEN:
            return
        ship = entity["ship"]
        base = visual.value["base"]
        ticks = visual.value["ticks"]
        base.opacity = 127
        base.x = window.window.width - 160
        base.y = 50
        base.draw()

        for i, tick in enumerate(ticks):
            lb = i * 20
            ub = i * 20 + 20
            ab = min(max(ship.boost, lb), ub)
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
        cp = entity["checkpoint"]
        physics = entity["physics"]
        arrow = entity["ui visual"].visuals[0].value

        zoom = window.camera_zoom

        if cp.is_next:
            arrow_x, arrow_y = world_to_screen(
                physics.position.x,
                physics.position.y,
                width,
                height,
                camera.x,
                camera.y,
                zoom,
            )

            half_sprite_x = 128 / zoom
            half_sprite_y = 128 / zoom

            # Check if original sprite was off the screen, and draw if so
            if (
                arrow_y < -half_sprite_y
                or arrow_y > half_sprite_y + height
                or arrow_x < -half_sprite_x
                or arrow_x > half_sprite_x + width
            ):
                # Clamp arrow to on the screen edge

                entity = get_ship_entity()
                ship_physics = entity["physics"]

                ship_x, ship_y = world_to_screen(
                    ship_physics.position.x,
                    ship_physics.position.y,
                    width,
                    height,
                    camera.x,
                    camera.y,
                    zoom,
                )

                arrow_point = V2(arrow_x, arrow_y)
                ship_point = V2(ship_x, ship_y)

                intersections = []

                intersections.append(
                    self.calculate_line_intersection(
                        ship_point, arrow_point, V2(-1.0, 0.0), height, vertical=False
                    )
                )

                intersections.append(
                    self.calculate_line_intersection(
                        ship_point, arrow_point, V2(1.0, 0.0), 0, vertical=False
                    )
                )

                intersections.append(
                    self.calculate_line_intersection(
                        ship_point, arrow_point, V2(0.0, -1.0), width, vertical=True
                    )
                )

                intersections.append(
                    self.calculate_line_intersection(
                        ship_point, arrow_point, V2(0.0, 1.0), 0, vertical=True
                    )
                )

                intersections = [(i, p) for i, p in intersections if p is not None]

                e = 1.0
                intersections = [
                    p
                    for i, p in intersections
                    if i
                    and (0 - e <= p.x <= width + e)
                    and (0 - e <= p.y <= height + e)
                ]

                if len(intersections) > 0:
                    v = physics.position - ship_physics.position
                    arrow.rotation = -(v.degrees)
                    arrow.x = intersections[0].x
                    arrow.y = intersections[0].y
                    arrow.draw()

    def update(self):
        ship_entity = get_ship_entity()
        window = get_window()

        self.render_bg(window)

        self.camera_offset(window)

        width, height = window.window.width, window.window.height
        pan_x, pan_y = window.camera_position.x, window.camera_position.y
        zoom = window.camera_zoom

        entities = Entity.with_component("game visual")
        visuals = []
        for entity in entities:
            for visual in entity["game visual"].visuals:
                visuals.append((entity, visual))

        for entity, visual in sorted(visuals, key=lambda x: x[1].z_sort):
            if visual.kind == "emitter":
                self.draw_emitter(window, entity, visual)
            elif visual.kind == "flare":
                self.draw_flare(window, entity, visual, ship_entity)
            elif visual.kind == "sprite":
                physics = entity["physics"]
                sprite = visual.value
                if physics is not None:
                    sprite.x = physics.position.x
                    sprite.y = physics.position.y
                    sprite.rotation = float(-physics.rotation)
                x, y = world_to_screen(
                    sprite.x, sprite.y,
                    width, height,
                    pan_x, pan_y,
                    zoom
                )
                s_w = sprite.width / 2 + 50
                s_h = sprite.height / 2 + 50
                if x + s_w > 0 and x - s_w < width and y + s_h > 0 and y - s_h < width:
                    sprite.draw()
            elif visual.kind == "flight path":
                self.draw_flight_path_line(window, entity, visual)
            elif visual.kind == "sprite batch":
                self.draw_sprite_batch(window, entity, visual)
            elif visual.kind == "tutorial text":
                self.draw_tutorial_text(window, entity, visual)

        self.reset_camera(window)

        entities = Entity.with_component("ui visual")
        visuals = []
        for entity in entities:
            for visual in entity["ui visual"].visuals:
                visuals.append((entity, visual))

        for entity, visual in sorted(visuals, key=lambda x: x[1].z_sort):
            if visual.kind == "checkpoint arrow":
                self.draw_checkpoint_arrow(window, entity, visual)
            elif visual.kind == "boost":
                self.draw_boost_meter(window, entity, visual)
            elif visual.kind == "label":
                self.draw_label(window, entity, visual)
            elif visual.kind == "real time label":
                self.draw_real_time_label(window, entity, visual)
            elif visual.kind == "menu options":
                self.draw_menu_options(window, entity, visual)
            elif visual.kind == "menu sprite":
                self.draw_menu_sprite(window, entity, visual)
            elif visual.kind == "menu description":
                self.draw_menu_description(window, entity, visual)

