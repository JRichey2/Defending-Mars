import sys
import pygame

from . import ecs


class Message(ecs.Event):
    message = ecs.field(type=str, mandatory=True)


class EventSystem(ecs.System):

    NAME = 'Event System'

    def update(self):
        '''Convert inputs to ECS messages for other systems'''

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                # This is an example of injecting an event.
                # Other systems can subscribe to events by kind
                ecs.System.inject(
                    Message(
                        kind='Key Press',
                        message=f'Key {event.key} was pressed'
                    )
                )

