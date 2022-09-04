import pygame

from . import ecs


class RenderSystem(ecs.System):

    NAME = 'Render System'

    def update(self):
        screen = list(ecs.Entity.with_component("screen"))[0]
        component = screen['screen']
        component.screen.blit(component.background, (0, 0))

        sprites = ecs.Entity.with_component("surface")
        for sprite in sprites:
            position = sprite['position']
            if position is None:
                continue
            surface = sprite['surface']
            component.screen.blit(surface.surface, (position.x, position.y))
        pygame.display.flip()

