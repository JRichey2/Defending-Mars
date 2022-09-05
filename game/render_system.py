import pygame

from . import ecs


class RenderSystem(ecs.System):

    def update(self):
        screen = list(ecs.Entity.with_component("screen"))[0]
        sc = screen['screen']
        camera = sc.camera_position
        viewport = sc.viewport_size

        sc.background.fill((0, 0, 0))

        sprites = ecs.Entity.with_component("surface")
        for sprite in sprites:
            position = sprite['position']
            if position is None:
                continue
            surface = sprite['surface']

            if position.rotate != 0.0 or surface.scale != 1.0:
                rotated_surface = pygame.transform.rotozoom(surface.surface, position.rotate, surface.scale)
                center = surface.surface.get_rect(center=position.position).center
                new_position = rotated_surface.get_rect(center=center)
                new_position.x -= camera.x
                new_position.y -= camera.y

                # Paralax scrolling
                if position.z_index != 0:
                    new_position.x = new_position.x // position.z_index
                    new_position.y = new_position.y // position.z_index

                sc.background.blit(rotated_surface, new_position)
            else:
                center = surface.surface.get_rect(center=position.position).center
                new_position = surface.surface.get_rect(center=center)
                new_position.x -= camera.x
                new_position.y -= camera.y

                # Paralax scrolling
                if position.z_index != 0:
                    new_position.x = new_position.x // position.z_index
                    new_position.y = new_position.y // position.z_index

                sc.background.blit(surface.surface, new_position)

            # special_flags=pygame.BLEND_ADD

        screen_rect = sc.screen.get_rect()
        sc_w = screen_rect.width
        sc_h = screen_rect.height
        sc_ar = sc_w / sc_h

        bg_rect = sc.background.get_rect()
        t_w = bg_rect.width
        t_h = bg_rect.height
        t_ar = t_w / t_h

        scale = t_ar / sc_ar

        # Vertical Bars
        if sc_ar > t_ar:
            sw = int(sc_w * scale)
            sh = sc_h
            ox = (sc_w - sw) // 2
            oy = 0

        # Horizontal Bars
        else:
            sw = sc_w
            sh = int(sc_w / t_ar)
            ox = 0
            oy = (sc_h - sh) // 2


        sc.screen.fill((0, 0, 0))
        scaled_bg = pygame.transform.smoothscale(sc.background, (sw, sh))
        sc.screen.blit(scaled_bg, (ox, oy))

        pygame.display.flip()

