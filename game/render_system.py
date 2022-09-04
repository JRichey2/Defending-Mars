import pygame

from . import ecs


class RenderSystem(ecs.System):

    def update(self):
        screen = list(ecs.Entity.with_component("screen"))[0]
        sc = screen['screen']
        paralax = 20
        sc.screen.blit(sc.background, (0, 0), area=(sc.x // paralax, sc.y  // paralax, sc.width, sc.height))

        sprites = ecs.Entity.with_component("surface")
        for sprite in sprites:
            position = sprite['position']
            if position is None:
                continue
            surface = sprite['surface']
            rotated_surface = pygame.transform.rotozoom(surface.surface, position.rotate, 0.25)
            new_position = rotated_surface.get_rect(center = surface.surface.get_rect(center = position.position).center)
            new_position.x -= sc.x
            new_position.y -= sc.y
            sc.screen.blit(rotated_surface, new_position)
            # special_flags=pygame.BLEND_ADD 
        pygame.display.flip()

