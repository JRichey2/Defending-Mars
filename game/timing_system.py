from . import ecs
from .ecs import Event, Entity
from . import settings
from pyglet import clock
import pyglet
from .components import UIVisualComponent
from .components import Visual
from .events import CountdownEvent
import time


class TimingSystem(ecs.System):

    def setup(self):
        self.subscribe('MapLoaded')
        self.subscribe('Countdown')
        self.countdown = ['3', '2', '1', 'GO']

    def initiate_gravity_acc(self, dt):
        settings.ACCELERATION = True
        settings.GRAVITY = True
        settings.BOOST = True
        start_time = time.monotonic()

    def update(self):
        events, self.events = self.events, []

        for event in events:
            print(event)
            if event.kind == 'MapLoaded':
                entity = Entity()
                self.selection_label_entity_id = entity.entity_id
                label = pyglet.text.Label('GET READY',
                            font_size=36,
                            x=500, y=500,
                            anchor_x="center", anchor_y="top")
                entity.attach(UIVisualComponent(
                    visuals=[
                        Visual(kind='label', z_sort=0, value=label)
                    ]
                ))
                clock.schedule_once(lambda x:ecs.System.inject(CountdownEvent(kind='Countdown', countdown_index=0)),2)
                clock.schedule_once(lambda x:ecs.System.inject(CountdownEvent(kind='Countdown', countdown_index=1)),3)
                clock.schedule_once(lambda x:ecs.System.inject(CountdownEvent(kind='Countdown', countdown_index=2)),4)
                clock.schedule_once(lambda x:ecs.System.inject(CountdownEvent(kind='Countdown', countdown_index=3)),5)
                clock.schedule_once(self.initiate_gravity_acc,5)
                clock.schedule_once(lambda x:ecs.Entity.find(self.selection_label_entity_id).destroy(),6)
            if event.kind == 'Countdown':
                countdown_index = event.countdown_index
                entity = ecs.Entity.find(self.selection_label_entity_id)
                label = entity['ui visual'].visuals[0].value
                label.text = self.countdown[countdown_index]

               