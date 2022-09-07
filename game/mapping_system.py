import pyglet
import sys
import json

from . import ecs
from itertools import cycle
from .components import (
    WindowComponent,
    SpriteComponent,
    PhysicsComponent,
    InputComponent,
    Emitter,
    EmitterBoost,
    FlightPath,
    Visual,
    GameVisualComponent,
    UIVisualComponent,
    EnemyComponent,
    MassComponent,
    BoostComponent,
    SpriteCheckpointComponent,
    CollisionComponent,
)

from .ecs import Entity, Event
from .assets import ASSETS
from .vector import V2


def create_sprite(position, rotation, image, scale=1.0, subpixel=True, z_sort=0.0):
    entity = Entity()
    entity.attach(PhysicsComponent(position=position, rotation=rotation))
    sprite=pyglet.sprite.Sprite(image, x=position.x, y=position.y, subpixel=subpixel)
    sprite.scale = scale
    sprite.rotation = rotation
    entity.attach(
        GameVisualComponent(
            visuals=[
                Visual(
                    kind="sprite",
                    z_sort=z_sort,
                    value=sprite
                )
            ]
        )
    )
    return entity


def create_flare(image, position):
    entity = Entity()
    entity.attach(PhysicsComponent(position=position))
    emitter = Emitter(image=image, batch=pyglet.graphics.Batch(), rate=0.1)
    visual = Visual(kind="emitter", z_sort=-100.0, value=emitter)
    entity.attach(GameVisualComponent(visuals=[visual]))
    return entity


class MappingSystem(ecs.System):

    def setup(self):
        self.subscribe('StartMapping')
        self.subscribe('StopMapping')
        self.subscribe('LoadMap')
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

            elif event.kind == 'LoadMap':
                self.load_map(event.map_name)

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

    def load_red_planet(self, position):
        entity = create_sprite(position, 0, ASSETS['red_planet'])
        entity.attach(MassComponent(mass=100))
        entity.attach(CollisionComponent(circle_radius=220))

    def load_moon(self, position):
        entity = create_sprite(position, 0, ASSETS['moon'])
        entity.attach(MassComponent(mass=15))
        entity.attach(CollisionComponent(circle_radius=56))

    def load_earth(self, position):
        entity = create_sprite(V2(1900.0, 2100.0), 0, ASSETS['earth'])
        entity.attach(MassComponent(mass=400))
        entity.attach(CollisionComponent(circle_radius=500))

    def load_map(self, map_name):

        with open(f"{map_name}_objects.json", "r") as f:
            map_objects_data = f.read()
        map_objects = json.loads(map_objects_data)

        for item in map_objects:
            if item['object'] == 'moon':
                self.load_moon(V2(item['x'], item['y']))
            elif item['object'] == 'earth':
                self.load_earth(V2(item['x'], item['y']))
            elif item['object'] == 'red_planet':
                self.load_red_planet(V2(item['x'], item['y']))

        flight_path = Entity()

        with open(f"{map_name}_path.json", "r") as f:
            map_path_data = f.read()
        map_path = json.loads(map_path_data)

        points = [V2(p['x'], p['y']) for p in map_path]
        checkpoints = [
            {
                'center': points[i],
                'rotation': (
                    (points[i + 1] - points[i]).degrees - 90
                    if i == 0 else
                    (points[i] - points[i - 1]).degrees - 90
                )
            }
            for i, p in enumerate(map_path)
            if 'checkpoint' in p
        ]

        for cp_order, checkpoint in enumerate(checkpoints):

            cp = Entity()

            position = checkpoint['center']
            rotation = checkpoint['rotation']
            cp.attach(PhysicsComponent(position=position, rotation=rotation))

            top_cp_image = 'checkpoint_top' if cp_order == 0 else 'checkpoint_next_top'
            top_cp_sprite=pyglet.sprite.Sprite(ASSETS[top_cp_image], x=position.x, y=position.y)

            bottom_cp_image = 'checkpoint_bottom' if cp_order == 0 else 'checkpoint_next_bottom'
            bottom_cp_sprite=pyglet.sprite.Sprite(ASSETS[bottom_cp_image], x=position.x, y=position.y)

            top_cp_sprite.rotation = rotation
            bottom_cp_sprite.rotation = rotation

            cp.attach(
                GameVisualComponent(
                    visuals=[
                        Visual(
                            kind="sprite",
                            z_sort=-9.0,
                            value=top_cp_sprite
                        ),
                        Visual(
                            kind="sprite",
                            z_sort=-12.0,
                            value=bottom_cp_sprite
                        ),
                    ]
                )
            )

            cp.attach(
                UIVisualComponent(
                    visuals=[
                        Visual(
                            kind="checkpoint arrow",
                            z_sort=1.0,
                            value=pyglet.sprite.Sprite(ASSETS['checkpoint_arrow']),
                        )
                    ]
                )
            )

            #TODO UI Visual cp.attach(create_sprite_locator(ASSETS['checkpoint_arrow']))
            cp.attach(SpriteCheckpointComponent(
                next_image_bottom=ASSETS['checkpoint_bottom'],
                passed_image_bottom=ASSETS['checkpoint_passed_bottom'],
                next_image_top=ASSETS['checkpoint_top'],
                passed_image_top=ASSETS['checkpoint_passed_top'],
                cp_order=cp_order,
            ))

        points_p = []
        for p in points:
            points_p.append(p.x)
            points_p.append(p.y)

        infinite_magenta = cycle((255, 0, 255, 50))
        flight_path.attach(
            GameVisualComponent(
                visuals=[
                    Visual(
                        kind='flight path',
                        z_sort=-100.0,
                        value = FlightPath(
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
                    )
                ]
            )
        )

        for i, point in enumerate(points):
            if i % 2 == 1:
                v = points[i] - points[i-1]
                a = V2.from_degrees_and_length(v.degrees + 90, 150) + point
                b = V2.from_degrees_and_length(v.degrees - 90, 150) + point
                create_flare(ASSETS['particle_flare'], a)
                create_flare(ASSETS['particle_flare'], b)

        player = ecs.Entity.with_component('input')[0]
        player['physics'].position = points[0].copy
        ecs.System.inject(Event(kind='CenterCamera'))



