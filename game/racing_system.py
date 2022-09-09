import json
import os
import pyglet
import time

from itertools import cycle

from . import settings
from .assets import ASSETS
from .common import get_ship_entity, get_window
from .components import (
    PhysicsComponent,
    GameVisualComponent,
    UIVisualComponent,
    CountdownComponent,
    Visual,
    FlightPath,
)
from .ecs import *
from .events import CountdownEvent, MapEvent
from .vector import *

from pyglet import clock


class RacingSystem(System):

    def setup(self):
        self.subscribe('MapLoaded')
        self.subscribe('RaceStart')
        self.subscribe('RaceComplete')

    def handle_event(self, event):
        if event.kind == 'MapLoaded':
            # Freeze the ship
            ship_entity = get_ship_entity()
            ship_entity['physics'].static = True

            # Create a countdown label
            countdown_entity = Entity()
            countdown_entity.attach(CountdownComponent(
                purpose="race",
                started_at=time.monotonic(),
                duration=6.0,
            ))
            window = get_window()
            x, y = window.window.width / 2, window.window.height
            label = pyglet.text.Label('GET READY', font_size=36, x=x, y=y, anchor_x="center", anchor_y="top")
            visual = Visual(kind='label', z_sort=0, value=label)
            countdown_entity.attach(UIVisualComponent(
                visuals=[visual],
                top = .90,
                right = 0.5,
            ))

            # Update the map component that was loaded to know about the countdown label
            map_entity = Entity.find(event.map_entity_id)
            map_ = map_entity['map']
            map_.race_countdown_id = countdown_entity.entity_id

            # Open the PB line file and load in the line
            with open(os.path.join('records', 'pb.json'), 'r') as f:
                map_.pb_racing_line = json.loads(f.read())

            map_.pb_line_entity_id = self.create_pb_line(map_)
            map_.pb_ghost_entity_id = self.create_pb_ghost()

        elif event.kind == 'RaceStart':
            # Unfreeze the ship
            ship_entity = get_ship_entity()
            ship_entity['physics'].static = False

            # Set the race start time if map exists
            map_entity = Entity.find(event.map_entity_id)
            if not map_entity:
                return
            map_ = map_entity["map"]
            start_time = time.monotonic()
            map_.race_start_time = start_time

            # Record the first racing line point
            self.record_racing_line_point(map_, start_time)

        elif event.kind == 'RaceComplete':
            # Update the race completion if the map exists
            map_entity = Entity.find(event.map_entity_id)
            if not map_entity:
                return
            self.update_race_completion(map_entity)

            # Record the final racing line point
            map_ = map_entity["map"]
            self.record_racing_line_point(map_, map_.race_end_time, final_point=True)
            with open(os.path.join('records', 'pb.json'), 'w') as f:
                f.write(json.dumps(map_.racing_line))

    def update(self):
        for map_entity in Entity.with_component("map"):
            self.update_countdown(map_entity)
            map_ = map_entity["map"]
            current_time = time.monotonic()
            if len(map_.racing_line) > 0:
                self.record_racing_line_point(map_, current_time)

            if map_.pb_ghost_entity_id is not None and map_.race_start_time is not None:
                self.update_ghost(map_, current_time)


    def update_ghost(self, map_, current_time):
        dt = current_time - map_.race_start_time
        points = enumerate(map_.pb_racing_line)
        ghost_point  = list(filter((lambda x: x[1]['dt'] > dt), points))

        # Ghost already finished the race
        if len(ghost_point) == 0:
            return

        i, p = ghost_point[0]
        ghost_entity = Entity.find(map_.pb_ghost_entity_id)
        # We didn't find a ghost, nothing to update
        if ghost_entity is None:
            return

        # Update the position and rotation of the ghost via interpolation
        physics = ghost_entity['physics']
        if i == 0:
            physics.position = V2(p['x'], p['y'])
            physics.rotation = p['r']
        else:
            p0 = map_.pb_racing_line[i - 1]
            p1 = p
            dt_t = p1['dt'] - p0['dt']
            dt_p = dt - p0['dt']
            a = dt_p / dt_t
            x = p0['x'] * (1 - a) + p1['x'] * a
            y = p0['y'] * (1 - a) + p1['y'] * a
            r = p0['r'] * (1 - a) + p1['r'] * a
            physics.position = V2(x, y)
            physics.rotation = r


    def update_countdown(self, map_entity):
        for entity in Entity.with_component("countdown"):
            countdown = entity["countdown"]
            map_ = map_entity["map"]

            if entity.entity_id != map_.race_countdown_id:
                continue

            if countdown.purpose != "race":
                continue

            if not map_entity["map"].is_active:
                print("Map is not active, destroying countdown")
                entity.destroy()

            label = entity["ui visual"].visuals[0].value

            time_left = (countdown.duration + countdown.started_at) - time.monotonic()
            if time_left > 3.0:
                label.text = "Get Ready!"
            elif time_left > 2.0:
                label.text = "3"
            elif time_left > 1.0:
                label.text = "2"
            elif time_left > 0.0:
                label.text = "1"
            elif time_left > -1.0:
                label.text = "Go"
                if not countdown.completed:
                    countdown.completed = True
                    System.inject(MapEvent(
                        kind='RaceStart',
                        map_name=map_entity['map'].map_name,
                        map_entity_id=map_entity.entity_id,
                    ))
            else:
                entity.destroy()

    def update_race_completion(self, map_entity):
        map_ = map_entity["map"]

        # Calculate race duration
        new_time = (map_.race_end_time - map_.race_start_time)

        # Read the current records
        with open(os.path.join('maps', 'map_record.json'), 'r') as f:
            data = json.loads(f.read())

        # Find the record we need to check
        for i, record in enumerate(data):
            if record['Map']== 'Default':
                map_index = i
                current_record = record['Record']

        # Check the record and update it if we've beaten it
        if new_time < current_record:
            print('NEW RECORD')
            data[map_index]['Record'] = new_time
            with open(os.path.join('maps','map_record.json'), 'w') as f:
                f.write(json.dumps(data, indent=2))

    def record_racing_line_point(self, map_, at_time, final_point=False):
        entity = get_ship_entity()
        position = entity['physics'].position
        rotation = entity['physics'].rotation

        if (len(map_.racing_line) == 0
                or (V2(map_.racing_line[-1]['x'],
                       map_.racing_line[-1]['y']) - position).length > 50
                or final_point):
            map_.racing_line.append({
                'x': position.x,
                'y': position.y,
                'r': rotation,
                'dt': at_time - map_.race_start_time,
            })


    def create_pb_ghost(self):
        entity = Entity()
        entity.attach(PhysicsComponent(position=V2(0, 0), rotation=0))
        sprite=pyglet.sprite.Sprite(ASSETS['base_ship'], x=0, y=0, subpixel=True)
        sprite.opacity = 127
        sprite.scale = 0.25
        game_visuals = [Visual(kind="sprite", z_sort=-10.0, value=sprite)]
        entity.attach(GameVisualComponent(visuals=game_visuals))
        return entity.entity_id

    def create_pb_line(self, map_):
        entity = Entity()
        points = [V2(p['x'], p['y']) for p in map_.pb_racing_line]
        points_p = []
        for p in points:
            points_p.append(p.x)
            points_p.append(p.y)

        infinite_magenta = cycle((255, 0, 255, 50))
        fp = FlightPath(
            path = points,
            points = pyglet.graphics.vertex_list(len(points),
                ('v2f', points_p),
                ('c4B', list(
                    y for x, y in
                    zip(
                        range(len(points) * 4),
                        infinite_magenta
                    )
                )),
            )
        )

        visuals=[Visual(kind='flight path', z_sort=-10.0, value=fp)]
        entity.attach(GameVisualComponent(visuals=visuals))
        return entity.entity_id

