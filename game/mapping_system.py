import os
import pyglet
import sys
import json
from . import settings
from .events import MapEvent

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
    MapComponent,
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
        self.subscribe('StartPlacements')
        self.subscribe('StopPlacements')
        self.subscribe('PlacementSelection')
        self.subscribe('Place')
        self.placement = False
        self.map_file = None
        self.last_mapped_point = None
        self.mapping = False
        self.selections = ['moon', 'red_planet', 'earth', 'checkpoint']
        self.selection_index = 0

    def update(self):
        events, self.events = self.events, []

        for event in events:

            if event.kind == 'StartMapping':
                print('Started Mapping')
                self.map_file = open(os.path.join('maps', 'wip_path.json'), 'w')
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
                self.clear_map()
                self.load_map(event.map_name)

            elif event.kind == 'StartPlacements':
                print('Started Placements')
                with open(os.path.join('maps', 'wip_objects.json'), 'r') as f:
                    data = f.read()
                self.placements = json.loads(data)
                self.placement = True
                settings.GRAVITY = False
                entity = Entity()
                self.selection_label_entity_id = entity.entity_id
                label = pyglet.text.Label(self.selections[self.selection_index],
                          font_size=36,
                          x=20, y=20,
                          anchor_x="left", anchor_y="bottom")
                entity.attach(UIVisualComponent(
                    visuals=[
                        Visual(kind='label', z_sort=0, value=label)
                    ]
                ))
                with open(os.path.join('maps', f"wip_path.json"), "r") as f:
                    map_path_data = f.read()
                self.flight_path = json.loads(map_path_data)

            elif event.kind == 'StopPlacements':
                print('Stopped Placements')
                settings.GRAVITY = True
                self.placement = False
                with open(os.path.join('maps', 'wip_objects.json'), 'w') as f:
                    f.write(json.dumps(self.placements, indent=2))
                with open(os.path.join('maps', 'wip_path.json'), 'w') as f:
                    f.write(json.dumps(self.flight_path, indent=2))
                ecs.System.inject(MapEvent(kind='LoadMap', map_name='wip'))
                ecs.Entity.find(self.selection_label_entity_id).destroy()

            elif self.placement == True and event.kind == 'Place':
                object_name = self.selections[self.selection_index]
                if object_name == 'checkpoint':
                    print('something')
                    points = [
                        ((event.position - V2(p['x'],p['y'])).length_squared, p)
                        for p in self.flight_path
                    ]
                    closest_distance = min(x[0] for x in points)
                    closest_point = [p for d, p in points if d == closest_distance][0]
                    if 'check_point' not in closest_point:
                        closest_point['checkpoint'] = True

                        point_index = self.flight_path.index(closest_point)
                        if point_index == 0:
                            p1 = self.flight_path[point_index + 1]
                            p2 = self.flight_path[point_index]
                        else:
                            p1 = self.flight_path[point_index]
                            p2 = self.flight_path[point_index - 1]

                        p1 = V2(p1['x'], p1['y'])
                        p2 = V2(p2['x'], p2['y'])
                        rotation = (p1 - p2).degrees - 90
                        num_points = sum(1 for p in self.flight_path if 'checkpoint' in p)
                        self.load_checkpoint(V2(closest_point['x'], closest_point['y']), rotation, num_points)
                else:
                    self.placements.append({"object": object_name, "x": event.position.x, "y": event.position.y})
                    getattr(self, "load_" + object_name)(event.position)


            elif self.placement == True and event.kind == 'PlacementSelection':
                if event.direction == 'up':
                    self.selection_index = (self.selection_index - 1) % len(self.selections)
                elif event.direction == 'down':
                    self.selection_index = (self.selection_index + 1) % len(self.selections)
                ecs.Entity.find(self.selection_label_entity_id)['ui visual'].visuals[0].value.text = self.selections[self.selection_index]

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
        entity = create_sprite(position, 0, ASSETS['earth'])
        entity.attach(MassComponent(mass=400))
        entity.attach(CollisionComponent(circle_radius=500))

    def load_checkpoint(self, position, rotation, cp_order):
        cp = Entity()

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

        cp.attach(SpriteCheckpointComponent(
            next_image_bottom=ASSETS['checkpoint_bottom'],
            passed_image_bottom=ASSETS['checkpoint_passed_bottom'],
            next_image_top=ASSETS['checkpoint_top'],
            passed_image_top=ASSETS['checkpoint_passed_top'],
            finish_image_top=ASSETS['checkpoint_finish_top'],
            finish_image_bottom=ASSETS['checkpoint_finish_bottom'],
            cp_order=cp_order,
        ))


    def clear_map(self):
        mass_entities = list(ecs.Entity.with_component("mass"))
        for entity in mass_entities:
            entity.destroy()

        ship_id = ecs.Entity.with_component("input")[0].entity_id

        physics_entities = list(ecs.Entity.with_component("physics"))
        for entity in physics_entities:
            if entity.entity_id != ship_id:
                entity.destroy()

        map_entities = list(ecs.Entity.with_component("map"))
        for entity in map_entities:
            entity.destroy()

    def load_map(self, map_name):
        with open(os.path.join('maps', f"{map_name}_objects.json"), "r") as f:
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

        with open(os.path.join('maps', f"{map_name}_path.json"), "r") as f:
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
            position = checkpoint['center']
            rotation = checkpoint['rotation']
            self.load_checkpoint(position, rotation, cp_order)

        points_p = []
        for p in points:
            points_p.append(p.x)
            points_p.append(p.y)

        infinite_magenta = cycle((255, 0, 255, 50))
        flight_path.attach(MapComponent(map_name=map_name))
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
                entity = create_flare(ASSETS['particle_flare'], a)
                entity = create_flare(ASSETS['particle_flare'], b)

        player = ecs.Entity.with_component('input')[0]
        player['physics'].position = points[0].copy
        ecs.System.inject(Event(kind='CenterCamera'))



