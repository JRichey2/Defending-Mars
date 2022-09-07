import sys
import json

from . import ecs
from .vector import V2


class MappingSystem(ecs.System):

    def setup(self):
        self.subscribe('StartMapping')
        self.subscribe('StopMapping')
        self.map_file = None
        self.last_mapped_point = None
        self.mapping = False


    def update(self):
        events, self.events = self.events, []

        for event in events:

            if event.kind == 'StartMapping':
                print('Started Mapping')
                self.map_file = open('map.json', 'w')
                self.mapping = True
                self.map_file.write('[')

            elif event.kind == 'StopMapping':
                print('Stopped Mapping')
                self.map_file.write('\n]')
                self.map_file.close()
                self.map_file = None
                self.last_mapped_point = None
                self.mapping = False

        if not self.mapping:
            return

        player = ecs.Entity.with_component('input')[0]
        position = player['physics'].position

        if self.last_mapped_point is None:
            self.map_file.write(f'\n    {{"x": {position.x:.0f}, "y": {position.y:.0f}}}')
            self.last_mapped_point = position.copy

        distance = (self.last_mapped_point - position).length
        if distance > 50:
            self.map_file.write(',')
            self.map_file.write(f'\n    {{"x": {position.x:.0f}, "y": {position.y:.0f}}}')
            self.last_mapped_point = position.copy




