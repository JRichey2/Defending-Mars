import os
from itertools import cycle
import pyglet
import sys
import json

from . import ecs
from . import settings
from .assets import ASSETS
from .common import get_ship_entity
from .components import (
    PhysicsComponent,
    Emitter,
    FlightPath,
    MapComponent,
    Visual,
    GameVisualComponent,
    UIVisualComponent,
    CheckpointComponent,
    CollisionComponent,
)
from .ecs import *
from .events import MapEvent
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


class CartographySystem(System):

    def setup(self):
        self.subscribe('StartMapping')
        self.subscribe('StopMapping')
        self.subscribe('LoadMap')
        self.subscribe('StartPlacements')
        self.subscribe('StopPlacements')
        self.subscribe('PlacementSelection')
        self.subscribe('Place')
        self.flight_points = None
        self.placement = False
        self.last_mapped_point = None
        self.mapping = False
        # Name, Mass, Collision Radius
        self.selections = [
            ('satellite', 5, 80),
            ('asteroid_small', 10, 60),
            ('asteroid_medium', 25, 100),
            ('asteroid_large', 50, 175),
            ('moon', 15, 56),
            ('red_planet', 100, 220),
            ('earth', 400, 500),
            ('dwarf_gas_planet', 40, 150),
            ('medium_gas_planet', 150, 240),
            ('gas_giant', 300, 500),
            ('black_hole', 1000, 332),
            ('checkpoint', None, None),
            ('boost_powerup', None, None),
            ('slowdown', None, None),
        ]
        self.selection_index = 0

    def handle_event(self, event):
        if event.kind == 'StartMapping':
            print('Started Mapping')
            self.flight_points = []
            self.mapping = True

        elif event.kind == 'StopMapping':
            print('Stopped Mapping')
            with open(os.path.join('maps', 'wip_path.json'), 'w') as f:
                f.write(json.dumps(self.flight_points ,indent=2))
            self.last_mapped_point = None
            self.mapping = False

        elif event.kind == 'LoadMap':
            self.clear_map()
            map_entity_id = self.load_map(event.map_name)
            System.inject(MapEvent(
                kind='MapLoaded',
                map_name=event.map_name,
                map_entity_id=map_entity_id)
            )

        elif event.kind == 'StartPlacements':
            print('Started Placements')
            with open(os.path.join('maps', 'wip_objects.json'), 'r') as f:
                data = f.read()
            self.placements = json.loads(data)
            self.placement = True
            settings.GRAVITY = False
            entity = Entity()
            self.selection_label_entity_id = entity.entity_id
            selection = self.selections[self.selection_index]
            label = pyglet.text.Label(selection[0],
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
            System.inject(MapEvent(kind='LoadMap', map_name='wip'))
            Entity.find(self.selection_label_entity_id).destroy()

        elif self.placement == True and event.kind == 'Place':
            object_name, mass, radius = self.selections[self.selection_index]
            if object_name == 'checkpoint':
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
                    self.load_checkpoint(V2(closest_point['x'], closest_point['y']), rotation, num_points, event.map_entity_id)
            elif mass is not None and radius is not None:
                self.placements.append({"object": object_name, "x": event.position.x, "y": event.position.y})
                self.load_object(object_name, event.position, mass, radius)


        elif self.placement == True and event.kind == 'PlacementSelection':
            if event.direction == 'up':
                self.selection_index = (self.selection_index - 1) % len(self.selections)
            elif event.direction == 'down':
                self.selection_index = (self.selection_index + 1) % len(self.selections)
            object_name, mass, radius = self.selections[self.selection_index]
            Entity.find(self.selection_label_entity_id)['ui visual'].visuals[0].value.text = object_name


    def update(self):
        if not self.mapping:
            return

        entity = get_ship_entity()
        position = entity['physics'].position

        if self.last_mapped_point is None:
            self.points.append({ "x": position.x, "y": position.y})
            self.last_mapped_point = position

        distance = (self.last_mapped_point - position).length
        if distance > 50:
            self.points.append({ "x": position.x, "y": position.y})
            self.last_mapped_point = position

    def load_object(self, name, position, mass, radius):
        entity = create_sprite(position, 0, ASSETS[name])
        entity.attach(PhysicsComponent(position=position, mass=mass))
        entity.attach(CollisionComponent(circle_radius=radius))

    def load_checkpoint(self, position, rotation, cp_order, map_entity_id):
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

        cp.attach(CheckpointComponent(
            next_image_bottom=ASSETS['checkpoint_bottom'],
            passed_image_bottom=ASSETS['checkpoint_passed_bottom'],
            next_image_top=ASSETS['checkpoint_top'],
            passed_image_top=ASSETS['checkpoint_passed_top'],
            finish_image_top=ASSETS['checkpoint_finish_top'],
            finish_image_bottom=ASSETS['checkpoint_finish_bottom'],
            cp_order=cp_order,
            map_entity_id=map_entity_id,
        ))


    def clear_map(self):
        old_maps = Entity.with_component("map")
        for old_map in old_maps:
            old_map['map'].is_active = False
            old_map.destroy()

        ship_id = get_ship_entity().entity_id

        physics_entities = list(Entity.with_component("physics"))
        for entity in physics_entities:
            if entity.entity_id != ship_id:
                entity.destroy()


    def load_map(self, map_name):
        map_entity = Entity()
        map_entity.attach(MapComponent(map_name=map_name))

        with open(os.path.join('maps', f"{map_name}_objects.json"), "r") as f:
            map_objects_data = f.read()
        map_objects = json.loads(map_objects_data)

        for item in map_objects:
            object_name, mass, radius = [
                s for s in self.selections
                if s[0] == item['object']
            ][0]
            position = V2(item['x'], item['y'])
            self.load_object(object_name, position, mass, radius)

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
            self.load_checkpoint(position, rotation, cp_order, map_entity.entity_id)

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

        flight_path.destroy()

        for i, point in enumerate(points):
            if i % 2 == 1:
                v = points[i] - points[i-1]
                a = V2.from_degrees_and_length(v.degrees + 90, 150) + point
                b = V2.from_degrees_and_length(v.degrees - 90, 150) + point
                entity = create_flare(ASSETS['particle_flare'], a)
                entity = create_flare(ASSETS['particle_flare'], b)

        entity = get_ship_entity()
        entity['physics'].position = points[0]
        System.inject(Event(kind='CenterCamera'))

        return map_entity.entity_id

