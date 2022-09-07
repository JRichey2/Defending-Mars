from . import ecs

import pyglet
import os


class RenderSystem(ecs.System):

    def update(self):
        window_entity = list(ecs.Entity.with_component("window"))[0]
        window = window_entity['window']
        camera = window.camera_position
        viewport = window.viewport_size
        width, height = window.window.width, window.window.height

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

            for ox in range(ixl, ixr + 1):
                for oy in range(ixb, ixt + 1):
                    sprite.x = width // 2 - camera.x // paralax + ox * sprite.width
                    sprite.y = height // 2 - camera.y // paralax + oy * sprite.height
                    sprite.draw()


        ox = width // 2 - camera.x
        oy = height // 2 - camera.y

        entities = ecs.Entity.with_component("emitter")
        for entity in entities:
            emitter = entity['emitter']
            for sprite in emitter.sprites:
                sprite.x += ox
                sprite.y += oy
            emitter.batch.draw()
            for sprite in emitter.sprites:
                sprite.x -= ox
                sprite.y -= oy

        entities = ecs.Entity.with_component("flight path")
        for entity in entities:
            flight_path = entity["flight path"]
            pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
            pyglet.gl.glHint(pyglet.gl.GL_LINE_SMOOTH_HINT, pyglet.gl.GL_NICEST)
            pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
            pyglet.gl.glTranslatef(ox, oy, 0.0)
            flight_path.points.draw(pyglet.gl.GL_LINE_STRIP)
            pyglet.gl.glLoadIdentity()

        entities = ecs.Entity.with_component("sprite")
        for entity in entities:
            physics = entity['physics']
            if physics is None:
                continue
            sprite = entity['sprite']
            sprite.x = physics.position.x + ox
            sprite.y = physics.position.y + oy
            sprite.rotation = float(-physics.rotation)
            sprite.draw()

        entities = ecs.Entity.with_component("boost")
        for entity in entities:
            boost = entity["boost"]
            boost.ui_base.opacity = 127
            boost.blend_src=pyglet.gl.GL_SRC_ALPHA,
            boost.blend_dest=pyglet.gl.GL_ONE,
            boost.ui_base.x = width - 160
            boost.ui_base.y = 50
            boost.ui_base.draw()

            for i, tick in enumerate(boost.ticks):
                lb = i * 20
                ub = i * 20 + 20
                ab = min(max(boost.boost, lb),ub)
                alpha = (ab - lb) / 20
                tick.opacity = int(127 * alpha)
                tick.x = width - 56
                tick.y = 34 + (i + 1) * 34
                tick.draw()

        # method for removing our checkpoint
        entities = ecs.Entity.with_component("checkpoint")
        checkpoint_order = 1000
        for entity in entities:
            sprite = entity['checkpoint']
            sprite_entity = entity['sprite']
            if sprite.completed == False:
                checkpoint_order = min(checkpoint_order, sprite.cp_order)
        
        for entity in entities:
            sprite = entity['checkpoint']
            sprite_entity = entity['sprite']
            if sprite.cp_order == checkpoint_order or sprite.cp_order == checkpoint_order +1:
                sprite_entity.image = sprite.next_image

        for entity in entities:
            sprite = entity['checkpoint']
            sprite_entity = entity['sprite']
            if sprite.completed == True:
                sprite_entity.image = sprite.passed_image
                
        for entity in entities:
            sprite = entity['checkpoint']
            physics = entity['physics']
            sprite_entity = entity['sprite']
            if camera.x >= physics.position.x - sprite_entity.width // 2 and camera.x <= physics.position.x + sprite_entity.width //2:
                if camera.y >= physics.position.y - sprite_entity.height // 2 and camera.y <= physics.position.y + sprite_entity.height //2:
                    if sprite.cp_order == checkpoint_order:
                        sprite.completed = True 
                        sprite.cp_order -= sprite.cp_order
                        checkpoint_order += 1

        entities = ecs.Entity.with_component("spritelocator")
        for entity in entities:
            locator = entity['spritelocator']
            physics = entity['physics']
            sprite = entity['sprite']
            sprite_checkpoint = entity['checkpoint']
            if sprite_checkpoint.completed == False and sprite_checkpoint.cp_order == checkpoint_order or sprite_checkpoint.cp_order == checkpoint_order +1:
                # ox/oy translates position to screen space
                x_ob = physics.position.x + ox
                y_ob = physics.position.y + oy
                half_sprite_x = sprite.width // 2
                half_sprite_y = sprite.height // 2
                half_locator_x = locator.width // 2
                half_locator_y = locator.height // 2

                # Check if original sprite was off the screen, and draw if so
                if (     y_ob < -half_sprite_y
                    or y_ob >  half_sprite_y + height
                    or x_ob < -half_sprite_x
                    or x_ob >  half_sprite_x + width):
                    # Clamp locator to on the screen edge
                    locator.x = min(max(x_ob, half_locator_x), width - half_locator_x)
                    locator.y = min(max(y_ob, half_locator_y), height - half_locator_y)
                    locator.draw()

