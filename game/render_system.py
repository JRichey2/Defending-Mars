from . import ecs


class RenderSystem(ecs.System):

    def update(self):
        screen = list(ecs.Entity.with_component("screen"))[0]
        sc = screen['screen']
        camera = sc.camera_position
        viewport = sc.viewport_size

        #sc.background.fill((0, 0, 0))

        entities = ecs.Entity.with_component("sprite")
        for entity in entities:
            physics = entity['physics']
            if physics is None:
                continue
            sprite = entity['sprite']

            # Paralax scrolling
            if physics.z_index != 0:
                sprite.x = (physics.position.x - camera.x - viewport.x / 2) / physics.z_index + viewport.x / 2
                sprite.y = (physics.position.y - camera.y - viewport.y / 2) / physics.z_index + viewport.y / 2
            else:
                sprite.x = (physics.position.x - camera.x)
                sprite.y = (physics.position.y - camera.y)

            sprite.rotation = float(-physics.rotation)

            sprite.draw()
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

