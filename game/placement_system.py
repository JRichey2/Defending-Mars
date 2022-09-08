from . import ecs
from .vector import V2


class PlacementSystem(ecs.System):

    def setup(self):
        self.subscribe('StartPlacements')
        self.subscribe('StopPlacements')
        self.subscribe('Place')
        self.placement_file = None
        self.placement = False

    def update(self):
        events, self.events = self.events, []

        for event in events:

            if event.kind == 'StartPlacements':
                print('Started Placements')
                self.placement_file = open('objects.json', 'w')
                self.placement = True
                self.placed_item = False
                self.placement_file.write('[')

            elif event.kind == 'StopPlacements':
                print('Stopped Placements')
                self.placement_file.write('\n]')
                self.placement_file.close()
                self.placement_file = None
                self.placement = False

            elif self.placement == True and event.kind == 'Place':
                if self.placed_item:
                    self.placement_file.write(',')
                self.placed_item = True
                self.placement_file.write(f'\n    {{"x": {event.position.x:.0f}, "y": {event.position.y:.0f}}}')


