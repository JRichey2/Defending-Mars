import pyglet
import os
import json
from itertools import cycle
from random import random

# ECS Import
from . import ecs
from .ecs import Entity, Event, field
from .vector import V2

# Component Imports
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

# System Imports
from .checkpoint_system import CheckpointSystem
from .event_system import EventSystem
from .render_system import RenderSystem
from .mapping_system import MappingSystem
from .physics_system import PhysicsSystem


# Global objects
RESOLUTION = V2(1920, 1080)


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


def create_sprite_checkpoint(image, subpixel=True):
    sprite=SpriteCheckpointComponent(image, subpixel=subpixel)
    return sprite


def load_image(asset_name, center=True, anchor_x=0, anchor_y=0):
    image = pyglet.image.load(os.path.join('assets', asset_name))
    if center:
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
    if anchor_x != 0:
        image.anchor_x = anchor_x
    if anchor_y != 0:
        image.anchor_y = anchor_y
    return image


class KeyEvent(Event):
    key_symbol = field(mandatory=True)
    pressed = field(type=bool, mandatory=True)


class MouseMotionEvent(Event):
    x = field(type=int, mandatory=True)
    y = field(type=int, mandatory=True)
    dx = field(type=int, mandatory=True)
    dy = field(type=int, mandatory=True)


class DefendingMarsWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assets = {}
        # Load all of our assets
        self.assets['star_field'] = load_image('starfield-2048x2048.png', center=False)
        self.assets['closer_stars'] = load_image('closer-stars-2048x2048.png', center=False)
        self.assets['nebula'] = load_image('nebula-2048x2048.png', center=False)
        self.assets['base_ship'] = load_image('ship-base-256x256.png')
        self.assets['enemy_ship'] = load_image('ship-speed-64x64.png')
        self.assets['red_planet'] = load_image('red-planet-512x512.png')
        self.assets['red_planet_shield'] = load_image('red-planet-shield-512x512.png')
        self.assets['moon'] = load_image('moon-128x128.png')
        self.assets['earth'] = load_image('earth-1024x1024.png')
        # self.assets['turret_base'] = load_image('turret-basic-base-64x64.png')
        # self.assets['turret_basic_cannon'] = load_image('turret-basic-cannon-64x64.png')
        self.assets['energy_particle_cyan'] = load_image('energy-particle-cyan-64x64.png')
        self.assets['energy_particle_red'] = load_image('energy-particle-red-64x64.png')
        self.assets['particle_flare'] = load_image('particle-flare-32x32.png')
        self.assets['boost_ui_base'] = load_image('boost-ui-base-288x64.png')
        self.assets['boost_tick_red'] = load_image('boost-tick-red-48x48.png')
        self.assets['boost_tick_blue'] = load_image('boost-tick-blue-48x48.png')
        self.assets['boost_tick_yellow'] = load_image('boost-tick-yellow-48x48.png')
        self.assets['checkpoint_arrow'] = load_image('checkpoint-arrow-128x128.png', anchor_x=128, anchor_y=64)
        self.assets['checkpoint_top'] = load_image('checkpoint-top-256x256.png')
        self.assets['checkpoint_bottom'] = load_image('checkpoint-bottom-256x256.png')
        self.assets['checkpoint_next_top'] = load_image('checkpoint-next-top-256x256.png')
        self.assets['checkpoint_next_bottom'] = load_image('checkpoint-next-bottom-256x256.png')
        self.assets['checkpoint_finish_top'] = load_image('checkpoint-finish-top-256x256.png')
        self.assets['checkpoint_finish_bottom'] = load_image('checkpoint-finish-bottom-256x256.png')
        self.assets['checkpoint_passed_top'] = load_image('checkpoint-passed-top-256x256.png')
        self.assets['checkpoint_passed_bottom'] = load_image('checkpoint-passed-bottom-256x256.png')

        # Create a home planet that will be set at a specific coordinate area
        self.red_planet_entity = create_sprite(V2(0.0, 0.0), 0, self.assets['red_planet'])

        # trying to create a sprite for the image I want to place later on
        self.red_planet_entity.attach(MassComponent(mass=100))
        self.red_planet_entity.attach(CollisionComponent(circle_radius=236))

        # Create a shield to go over the planet entity. This will need to be callable some other way for a power up and coordinate location
        self.red_planet_shield_entity = create_sprite(V2(0.0, 0.0), 0, self.assets['red_planet_shield'])

        # we could probably create a def function to create these based on a series of coords
        # Create a moon for a specific location number 1
        self.moon_planet_entity_1 = create_sprite(V2(-715.0, -350.0), 0, self.assets['moon'])
        self.moon_planet_entity_1.attach(MassComponent(mass=15))
        self.moon_planet_entity_1.attach(CollisionComponent(circle_radius=56))

        # Create a moon for a specific location number 2
        self.moon_planet_entity_2 = create_sprite(V2(-890.0, 20.0), 0, self.assets['moon'])
        self.moon_planet_entity_2.attach(MassComponent(mass=15))
        self.moon_planet_entity_2.attach(CollisionComponent(circle_radius=56))

        # Create a moon for a specific location number 3
        self.moon_planet_entity_3 = create_sprite(V2(-600.0, 460.0), 0, self.assets['moon'])
        self.moon_planet_entity_3.attach(MassComponent(mass=15))
        self.moon_planet_entity_3.attach(CollisionComponent(circle_radius=56))

        # Create a moon for a specific location number 4
        self.moon_planet_entity_4 = create_sprite(V2(-600.0, 800.0), 0, self.assets['moon'])
        self.moon_planet_entity_4.attach(MassComponent(mass=15))
        self.moon_planet_entity_4.attach(CollisionComponent(circle_radius=56))

        # Create a moon for a specific location number 5
        self.moon_planet_entity_5 = create_sprite(V2(260.0, 1642.0), 0, self.assets['moon'])
        self.moon_planet_entity_5.attach(MassComponent(mass=15))
        self.moon_planet_entity_5.attach(CollisionComponent(circle_radius=56))

        # Create a moon for a specific location number 6
        self.moon_planet_entity_6 = create_sprite(V2(900.0, 1847.0), 0, self.assets['moon'])
        self.moon_planet_entity_6.attach(MassComponent(mass=15))
        self.moon_planet_entity_6.attach(CollisionComponent(circle_radius=56))

        # Large Planet 1
        self.large_planet_1 = create_sprite(V2(246.0, 1136.0), 0, self.assets['red_planet'])
        self.large_planet_1.attach(MassComponent(mass=100))
        self.large_planet_1.attach(CollisionComponent(circle_radius=236))

        # Earth Planet 1
        self.earth = create_sprite(V2(1900.0, 2100.0), 0, self.assets['earth'])
        self.earth.attach(MassComponent(mass=400))
        self.earth.attach(CollisionComponent(circle_radius=500))

        self.flight_path_1 = Entity()

        with open("map.json", "r") as f:
            map_data = f.read()

        map = json.loads(map_data)

        points = [V2(p['x'], p['y']) for p in map]
        checkpoints = [
            {
                'center': points[i],
                'rotation': (
                    (points[i + 1] - points[i]).degrees - 90
                    if i == 0 else
                    (points[i] - points[i - 1]).degrees - 90
                )
            }
            for i, p in enumerate(map)
            if 'checkpoint' in p
        ]

        for cp_order, checkpoint in enumerate(checkpoints):

            cp = Entity()

            position = checkpoint['center']
            rotation = checkpoint['rotation']
            cp.attach(PhysicsComponent(position=position, rotation=rotation))

            top_cp_image = 'checkpoint_top' if cp_order == 0 else 'checkpoint_next_top'
            top_cp_sprite=pyglet.sprite.Sprite(self.assets[top_cp_image], x=position.x, y=position.y)

            bottom_cp_image = 'checkpoint_bottom' if cp_order == 0 else 'checkpoint_next_bottom'
            bottom_cp_sprite=pyglet.sprite.Sprite(self.assets[bottom_cp_image], x=position.x, y=position.y)

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
                            value=pyglet.sprite.Sprite(self.assets['checkpoint_arrow']),
                        )
                    ]
                )
            )

            #TODO UI Visual cp.attach(create_sprite_locator(self.assets['checkpoint_arrow']))
            cp.attach(SpriteCheckpointComponent(
                next_image_bottom=self.assets['checkpoint_bottom'],
                passed_image_bottom=self.assets['checkpoint_passed_bottom'],
                next_image_top=self.assets['checkpoint_top'],
                passed_image_top=self.assets['checkpoint_passed_top'],
                cp_order=cp_order,
            ))

        # Create a ship entity that we can control
        self.ship_entity = create_sprite(points[0].copy, 0, self.assets['base_ship'], 0.25, z_sort=-10.0)
        self.ship_entity.attach(InputComponent())
        emitter = EmitterBoost(
            image=self.assets['energy_particle_cyan'],
            boost_image=self.assets['energy_particle_red'],
            batch=pyglet.graphics.Batch(),
            rate=0.1,
        )
        visual = Visual(kind="emitter", z_sort=-11.0, value=emitter)
        self.ship_entity['game visual'].visuals.append(visual)
        self.ship_entity.attach(CollisionComponent(circle_radius=24))
        self.ship_entity.attach(BoostComponent())
        boost_visual = {
            'base': pyglet.sprite.Sprite(self.assets['boost_ui_base']),
            'ticks': [
                pyglet.sprite.Sprite(self.assets['boost_tick_red']),
                pyglet.sprite.Sprite(self.assets['boost_tick_yellow']),
                pyglet.sprite.Sprite(self.assets['boost_tick_yellow']),
                pyglet.sprite.Sprite(self.assets['boost_tick_yellow']),
                pyglet.sprite.Sprite(self.assets['boost_tick_yellow']),
                pyglet.sprite.Sprite(self.assets['boost_tick_blue']),
                pyglet.sprite.Sprite(self.assets['boost_tick_blue']),
                pyglet.sprite.Sprite(self.assets['boost_tick_blue']),
                pyglet.sprite.Sprite(self.assets['boost_tick_blue']),
                pyglet.sprite.Sprite(self.assets['boost_tick_blue']),
            ]
        }
        boost_visuals = [Visual(kind='boost', z_sort=0.0, value=boost_visual)]
        self.ship_entity.attach(UIVisualComponent(visuals=boost_visuals))


        points_p = []
        for p in points:
            points_p.append(p.x)
            points_p.append(p.y)

        infinite_magenta = cycle((255, 0, 255, 50))
        self.flight_path_1.attach(
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
        #self.flight_path_1.attach(GameVisualComponent(kind="flight path"))


        for i, point in enumerate(points):
            if i % 2 == 1:
                v = points[i] - points[i-1]
                a = V2.from_degrees_and_length(v.degrees + 90, 150) + point
                b = V2.from_degrees_and_length(v.degrees - 90, 150) + point
                create_flare(self.assets['particle_flare'], a)
                create_flare(self.assets['particle_flare'], b)

    def on_key_press(self, symbol, modifiers):
        ecs.System.inject(KeyEvent(kind='Key', key_symbol=symbol, pressed=True))

    def on_key_release(self, symbol, modifiers):
        ecs.System.inject(KeyEvent(kind='Key', key_symbol=symbol, pressed=False))

    def on_mouse_motion(self, x, y, dx, dy):
        ecs.System.inject(MouseMotionEvent(kind='MouseMotion', x=x, y=y, dx=dx, dy=dy))

    def on_close(self):
        ecs.System.inject(Event(kind='Quit'))


def run_game():

    # Initialize our systems in the order we want them to run
    # Events should come first, so we can react to input as 
    # quikli as possible
    EventSystem()

    # Physics system handles movement an collision
    PhysicsSystem()

    # Updates checkpoints
    CheckpointSystem()

    # Temporary for us to create maps with
    MappingSystem()

    # The render system draws things to the Window
    RenderSystem()

    # Create a Window entity
    window_entity = Entity()
    window=DefendingMarsWindow(1280, 720, resizable=True)

    window_entity.attach(WindowComponent(
        window=window,
        viewport_size=RESOLUTION,
        background_layers = [
            SpriteComponent(window.assets['star_field'], x=0, y=0),
            SpriteComponent(window.assets['closer_stars'], x=0, y=0),
            SpriteComponent(window.assets['nebula'], x=0, y=0),
        ]
    ))
    window.ship_entity.attach(BoostComponent())
    window_entity['window'].camera_position = window.ship_entity['physics'].position.copy

    def update(dt, *args, **kwargs):
        ecs.DELTA_TIME = dt
        window.clear()
        ecs.System.update_all()

    # Music: https://www.chosic.com/free-music/all/
    # background_audio = pyglet.media.load(os.path.join('assets', 'background_music_test.mp3'))

    # player = pyglet.media.Player()
    # player.loop = True
    # player.queue(background_audio)
    # player.play()

    pyglet.clock.schedule(update, 1/60.0)
    pyglet.app.run()

