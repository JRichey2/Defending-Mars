import pygame

from . import ecs


class RenderSystem(ecs.System):

    NAME = 'Render System'

    def update(self):
        screen = list(ecs.Entity.with_component("Screen Component"))[0]
        component = [c for c in screen.components if c.component_name == 'Screen Component'][0]
        component.screen.blit(component.background, (0, 0))

        sprites = ecs.Entity.with_component("Surface Component")
        for sprite in sprites:
            position = [c for c in sprite.components if c.component_name == 'Position Component']
            if len(position) == 0:
                continue
            position = position[0]    
            surface = [c for c in sprite.components if c.component_name == 'Surface Component'][0]
            component.screen.blit(surface.surface, (position.x, position.y))
        pygame.display.flip()

