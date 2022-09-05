import sys
import pygame

from game import input_component

from . import ecs


class Keypress(ecs.Event):
    key = ecs.field(type=str, mandatory=True)
    press = ecs.field(type=bool, mandatory=True)


class EventSystem(ecs.System):

    def update(self):
        '''Convert inputs to ECS messages for other systems'''

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit(0)

            if (event.type in (pygame.KEYDOWN, pygame.KEYUP) and
                    event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_q, pygame.K_e)):
                inputs = ecs.Entity.with_component("input")
                for i in inputs:
                    ic = i['input']
                    pressed = event.type == pygame.KEYDOWN
                    if event.key == pygame.K_w:
                        ic.w = pressed
                    elif event.key == pygame.K_a:
                        ic.a = pressed
                    elif event.key == pygame.K_s:
                        ic.s = pressed
                    elif event.key == pygame.K_d:
                        ic.d = pressed
                    elif event.key == pygame.K_q:
                        ic.q = pressed
                    elif event.key == pygame.K_e:
                        ic.e = pressed
                    #print(i, ic)
