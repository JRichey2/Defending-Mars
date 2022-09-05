from . import ecs


class RenderSystem(ecs.System):

    def update(self):
        screen = list(ecs.Entity.with_component("screen"))[0]
        sc = screen['screen']
        camera = sc.camera_position
        viewport = sc.viewport_size

        #sc.background.fill((0, 0, 0))

        sprites = ecs.Entity.with_component("sprite")
        for sprite in sprites:
            position = sprite['position']
            if position is None:
                continue
            sprite_comp = sprite['sprite']

            # Paralax scrolling
            if position.z_index != 0:
                sprite_comp.sprite.x = (position.position.x - camera.x - viewport.x / 2) / position.z_index + viewport.x / 2
                sprite_comp.sprite.y = (position.position.y - camera.y - viewport.y / 2) / position.z_index + viewport.y / 2
            else:
                sprite_comp.sprite.x = (position.position.x - camera.x)
                sprite_comp.sprite.y = (position.position.y - camera.y)

            sprite_comp.sprite.scale = sprite_comp.scale
            sprite_comp.sprite.rotation = float(-position.rotate)

            sprite_comp.sprite.draw()
            #sc.background.blit(surface.surface, new_position)

        #sc_w = sc.screen.width
        #sc_h = sc.screen.height
        #sc_ar = sc_w / sc_h

        #t_w = sc.background.width
        #t_h = sc.background.height
        #t_ar = t_w / t_h

        #scale = t_ar / sc_ar

        # Vertical Bars
        #if sc_ar > t_ar:
            #sw = int(sc_w * scale)
            #sh = sc_h
            #ox = (sc_w - sw) // 2
            #oy = 0

        # Horizontal Bars
        #else:
            #sw = sc_w
            #sh = int(sc_w / t_ar)
            #ox = 0
            #oy = (sc_h - sh) // 2


        #sc.screen.fill((0, 0, 0))
        #scaled_bg = scale to (sw, sh)
        #sc.screen.blit(scaled_bg, (ox, oy))

