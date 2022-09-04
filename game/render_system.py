import sys
import pygame

from . import ecs


class RenderSystem(ecs.System):

    NAME = 'Render System'

    def setup(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((250, 250, 250))
        font = pygame.font.Font(None, 36)
        text = font.render("Well, Hello There!", 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        self.background.blit(text, textpos)

    def update(self):
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

