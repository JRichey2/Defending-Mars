from . import ecs
import os
import json
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
        self.subscribe('MapComplete')
        self.subscribe('Countdown')
        self.countdown = ['3', '2', '1', 'GO']

    def initiate_gravity_acc(self, dt):
        settings.ACCELERATION = True
        settings.GRAVITY = True
        settings.BOOST = True
        timer = time.monotonic()
        ship = ecs.Entity.with_component("map timer")[0]
        ship['map timer'].start_time = timer

    def update(self):
        events, self.events = self.events, []

        window_entity = ecs.Entity.with_component("window")[0]
        window = window_entity['window']
        x_half = window.window.width // 2

        for event in events:

            if event.kind == 'MapLoaded':
                entity = Entity()
                self.selection_label_entity_id = entity.entity_id
                label = pyglet.text.Label('GET READY',
                            font_size=36,
                            x=x_half, y=window.window.height,
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
                clock.schedule_once(lambda x:ecs.System.inject(ecs.Event(kind='RaceStart')), 6)

            elif event.kind == 'Countdown':
                countdown_index = event.countdown_index
                entity = ecs.Entity.find(self.selection_label_entity_id)
                label = entity['ui visual'].visuals[0].value
                label.text = self.countdown[countdown_index]

            if event.kind == 'MapComplete':
                ship = ecs.Entity.with_component("map timer")[0]
                new_time = (ship['map timer'].end_time - ship['map timer'].start_time)
                with open(os.path.join('maps', 'map_record.json'), 'r') as f:
                    data = json.loads(f.read())
                for i, record in enumerate(data):
                    if record['Map']== 'Default':
                        map_index = i
                        current_record = record['Record']
                if new_time < current_record:
                    print('NEW RECORD')
                    data[map_index]['Record'] = new_time
                    with open(os.path.join('maps','map_record.json'), 'w') as f:
                        f.write(json.dumps(data, indent=2))

            elif event.kind == 'RaceStart':
                entity = ecs.Entity.find(self.selection_label_entity_id)
                if entity:
                    entity.destroy()

