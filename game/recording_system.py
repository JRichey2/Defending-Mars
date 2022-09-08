import pyglet
from itertools import cycle
import time
import os
import json

from . import ecs
from .assets import ASSETS
from .vector import V2
from .components import (
    FlightPath,
    GameVisualComponent,
    Visual,
    BoostComponent,
    PhysicsComponent
)


class RecordingSystem(ecs.System):

    def setup(self):
        self.subscribe('MapLoaded')
        self.subscribe('Countdown')
        self.subscribe('MapComplete')
        self.start_time = None
        self.points = None
        self.last_mapped_point = None
        self.flight_path_entity_id = None
        self.ghost_entity_id = None

    def record_point(self, at_time, final_point=False):
        if self.points is None:
            return

        ship = ecs.Entity.with_component("input")[0]
        position = ship['physics'].position
        rotation = ship['physics'].rotation

        if (len(self.points) == 0
                or (self.last_mapped_point - position).length > 50
                or final_point):
            self.points.append({
                'x': position.x,
                'y': position.y,
                'r': rotation,
                'dt': at_time - self.start_time,
            })
            self.last_mapped_point = position.copy


    def create_pb_line(self):
        if self.flight_path_entity_id is not None:
            ecs.Entity.find(self.flight_path_entity_id).destroy()
            self.flight_path_entity_id = None

        entity = ecs.Entity()
        points = [V2(p['x'], p['y']) for p in self.pb_points]
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
        self.flight_path_entity_id = entity.entity_id

    def create_pb_ghost(self):
        if self.ghost_entity_id is not None:
            ecs.Entity.find(self.ghost_entity_id).destroy()
        entity = ecs.Entity()
        entity.attach(PhysicsComponent(position=V2(0, 0), rotation=0))
        sprite=pyglet.sprite.Sprite(ASSETS['base_ship'], x=0, y=0, subpixel=True)
        sprite.opacity = 127
        sprite.scale = 0.25
        game_visuals = [
            Visual(kind="sprite", z_sort=-10.0, value=sprite),
        ]
        entity.attach(GameVisualComponent(visuals=game_visuals))
        self.ghost_entity_id = entity.entity_id

    def update_ghost(self, current_time):
        dt = current_time - self.start_time
        points = enumerate(self.pb_points)
        ghost_point  = list(filter((lambda x: x[1]['dt'] > dt), points))
        if len(ghost_point) == 0:
            # Ghost already finished the race
            return
        i, p = ghost_point[0]
        ghost = ecs.Entity.find(self.ghost_entity_id)
        if ghost is None:
            return
        physics = ghost['physics']
        if i == 0:
            physics.position = V2(p['x'], p['y'])
            physics.rotation = p['r']
        else:
            p0 = self.pb_points[i - 1]
            p1 = p
            dt_t = p1['dt'] - p0['dt']
            dt_p = dt - p0['dt']
            a = dt_p / dt_t
            x = p0['x'] * (1 - a) + p1['x'] * a
            y = p0['y'] * (1 - a) + p1['y'] * a
            r = p0['r'] * (1 - a) + p1['r'] * a
            physics.position = V2(x, y)
            physics.rotation = r


    def update(self):
        events, self.events = self.events, []

        for event in events:
            if event.kind == 'Countdown':
                if event.countdown_index == 0:
                    with open(os.path.join('records', 'pb.json'), 'r') as f:
                        self.pb_points = json.loads(f.read())
                    self.create_pb_line()
                    self.create_pb_ghost()
                elif event.countdown_index == 3:
                    self.start_time = time.monotonic()
                    self.points = []
                    self.record_point(self.start_time)
            elif event.kind == 'MapComplete':
                self.record_point(time.monotonic(), final_point=True)
                with open(os.path.join('records', 'pb.json'), 'w') as f:
                    f.write(json.dumps(self.points))
                self.points = None
                self.start_time = None
                self.last_mapped_point = None
            elif event.kind == 'MapLoaded':
                self.points = None
                self.start_time = None
                self.last_mapped_point = None

        if self.start_time is None:
            return

        current_time = time.monotonic()
        self.record_point(current_time)

        if self.ghost_entity_id is not None:
            self.update_ghost(current_time)

