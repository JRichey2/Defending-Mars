import sys
import pygame

from . import ecs


class RenderSystem(ecs.System):

    NAME = 'Render System'

    def update(self):
        screens = ecs.Entity.with_component("Screen Component")
        for screen in screens:
            component = [c for c in screen.components if c.component_name == 'Screen Component'][0]
            component.screen.blit(component.background, (0, 0))
            pygame.display.flip()

