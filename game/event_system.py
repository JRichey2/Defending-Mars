import sys
import pygame

from game import input_component

from . import ecs


class Keypress(ecs.Event):
    key = ecs.field(type=str, mandatory=True)
    press = ecs.field(type=bool, mandatory=True)


class EventSystem(ecs.System):

    NAME = 'Event System'

    def update(self):
        '''Convert inputs to ECS messages for other systems'''

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit(0)

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):

                # This is an example of injecting an event.
                # Other systems can subscribe to events by kind


                if event.key == pygame.K_w:
                    inputs = ecs.Entity.with_component("Input Component")
                    for i in inputs:
                        ic = [c for c in i.components if c.component_name == 'Input Component'][0]
                        ic.w = event.type == pygame.KEYDOWN 
                        print(i, ic)
                elif event.key == pygame.K_a:
                    inputs = ecs.Entity.with_component("Input Component")
                    for i in inputs:
                        ic = [c for c in i.components if c.component_name == 'Input Component'][0]
                        ic.a = event.type == pygame.KEYDOWN 
                        print(i, ic)
                elif event.key == pygame.K_s:
                    inputs = ecs.Entity.with_component("Input Component")
                    for i in inputs:
                        ic = [c for c in i.components if c.component_name == 'Input Component'][0]
                        ic.s = event.type == pygame.KEYDOWN 
                        print(i, ic)
                elif event.key == pygame.K_d:
                    inputs = ecs.Entity.with_component("Input Component")
                    for i in inputs:
                        ic = [c for c in i.components if c.component_name == 'Input Component'][0]
                        ic.d = event.type == pygame.KEYDOWN 
                        print(i, ic)