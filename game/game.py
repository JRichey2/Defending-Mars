import pyglet
import os
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
    EmitterBoostComponent,
    FlightPathComponent,
    SpriteComponentLocator,
    EnemyComponent,
    MassComponent,
    BoostComponent,
    SpriteCheckpointComponent,
)

# System Imports
from .event_system import EventSystem
from .render_system import RenderSystem
from .physics_system import PhysicsSystem


# Global objects
RESOLUTION = V2(1920, 1080)


def create_sprite(position, rotation, image, scale=1.0, subpixel=True):
    entity = Entity()
    entity.attach(PhysicsComponent(position=position, rotation=rotation))
    sprite=SpriteComponent(image, x=position.x, y=position.y, subpixel=subpixel)
    sprite.scale = scale
    sprite.rotation = rotation
    entity.attach(sprite)
    return entity

def create_sprite_locator(image, scale=1.0, subpixel=True):
    sprite=SpriteComponentLocator(image, subpixel=subpixel)
    sprite.scale = scale 
    return sprite

def create_sprite_checkpoint(image, subpixel=True):
    sprite=SpriteCheckpointComponent(image, subpixel=subpixel)
    return sprite

def load_image(asset_name, center=True):
    print(f"loading image {asset_name}")
    image = pyglet.image.load(os.path.join('assets', asset_name))
    if center:
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
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
        self.assets['boost_ui_base'] = load_image('boost-ui-base-288x64.png')
        self.assets['boost_tick_red'] = load_image('boost-tick-red-48x48.png')
        self.assets['boost_tick_blue'] = load_image('boost-tick-blue-48x48.png')
        self.assets['boost_tick_yellow'] = load_image('boost-tick-yellow-48x48.png')
        self.assets['checkpoint_top'] = load_image('checkpoint-top-128x128.png')
        self.assets['checkpoint_bottom'] = load_image('checkpoint-bottom-128x128.png')
        self.assets['checkpoint_next_top'] = load_image('checkpoint-next-top-128x128.png')
        self.assets['checkpoint_next_bottom'] = load_image('checkpoint-next-bottom-128x128.png')

        # Create a home planet that will be set at a specific coordinate area
        self.red_planet_entity = create_sprite(V2(0.0, 0.0), 0, self.assets['red_planet'])

        # trying to create a sprite for the image I want to place later on
        self.red_planet_entity.attach(create_sprite_locator(self.assets['red_planet'], 0.125))
        self.red_planet_entity.attach(MassComponent(mass=100))

        # Create a shield to go over the planet entity. This will need to be callable some other way for a power up and coordinate location
        self.red_planet_shield_entity = create_sprite(V2(0.0, 0.0), 0, self.assets['red_planet_shield'])
        self.red_planet_shield_entity.attach(create_sprite_locator(self.assets['red_planet_shield'], 0.125))

        # we could probably create a def function to create these based on a series of coords
        # Create a moon for a specific location number 1
        self.moon_planet_entity_1 = create_sprite(V2(-715.0, -350.0), 0, self.assets['moon'])
        self.moon_planet_entity_1.attach(create_sprite_locator(self.assets['moon'], 0.50))
        self.moon_planet_entity_1.attach(MassComponent(mass=15))

        # Create a moon for a specific location number 2
        self.moon_planet_entity_2 = create_sprite(V2(-890.0, 20.0), 0, self.assets['moon'])
        self.moon_planet_entity_2.attach(create_sprite_locator(self.assets['moon'], 0.50))
        self.moon_planet_entity_2.attach(MassComponent(mass=15))

        # Create a moon for a specific location number 3
        self.moon_planet_entity_3 = create_sprite(V2(-600.0, 460.0), 0, self.assets['moon'])
        self.moon_planet_entity_3.attach(create_sprite_locator(self.assets['moon'], 0.50))
        self.moon_planet_entity_3.attach(MassComponent(mass=15))

        # Create a moon for a specific location number 4
        self.moon_planet_entity_4 = create_sprite(V2(-600.0, 800.0), 0, self.assets['moon'])
        self.moon_planet_entity_4.attach(create_sprite_locator(self.assets['moon'], 0.50))
        self.moon_planet_entity_4.attach(MassComponent(mass=15))

        # Create a moon for a specific location number 5
        self.moon_planet_entity_5 = create_sprite(V2(260.0, 1642.0), 0, self.assets['moon'])
        self.moon_planet_entity_5.attach(create_sprite_locator(self.assets['moon'], 0.50))
        self.moon_planet_entity_5.attach(MassComponent(mass=15))

        # Create a moon for a specific location number 6
        self.moon_planet_entity_6 = create_sprite(V2(900.0, 1847.0), 0, self.assets['moon'])
        self.moon_planet_entity_6.attach(create_sprite_locator(self.assets['moon'], 0.50))
        self.moon_planet_entity_6.attach(MassComponent(mass=15))

        # Large Planet 1
        self.large_planet_1 = create_sprite(V2(246.0, 1136.0), 0, self.assets['red_planet'])
        self.large_planet_1.attach(create_sprite_locator(self.assets['red_planet'], 0.25))
        self.large_planet_1.attach(MassComponent(mass=100))

        # Earth Planet 1
        self.earth = create_sprite(V2(1900.0, 2100.0), 0, self.assets['earth'])
        self.earth.attach(create_sprite_locator(self.assets['earth'], 0.0625))
        self.earth.attach(MassComponent(mass=400))

        # Checkpoint 1 top test
        self.checkpoint_top = create_sprite(V2(-996.0, 93.9), 0, self.assets['checkpoint_top'])
        self.checkpoint_top.attach(create_sprite_checkpoint(self.assets['checkpoint_top']))

        # Checkpoint 1 bottom test
        self.checkpoint_bottom = create_sprite(V2(-996.0, 94.1), 0, self.assets['checkpoint_bottom'])
        self.checkpoint_bottom.attach(create_sprite_checkpoint(self.assets['checkpoint_bottom']))

        # Checkpoint 2 top test
        self.checkpoint_top2 = create_sprite(V2(-708.0, -500.1), 0, self.assets['checkpoint_next_top'])
        self.checkpoint_top2.attach(create_sprite_checkpoint(self.assets['checkpoint_next_top']))

        # Checkpoint 2 bottom test
        self.checkpoint_bottom2 = create_sprite(V2(-708.0, -499.9), 0, self.assets['checkpoint_next_bottom'])
        self.checkpoint_bottom2.attach(create_sprite_checkpoint(self.assets['checkpoint_next_bottom']))

        # Checkpoint 3 top test
        self.checkpoint_top3 = create_sprite(V2(-600.0, 599.9), 0, self.assets['checkpoint_next_top'])
        self.checkpoint_top3.attach(create_sprite_checkpoint(self.assets['checkpoint_next_top']))

        # Checkpoint 3 bottom test
        self.checkpoint_bottom3 = create_sprite(V2(-600.0, 600.1), 0, self.assets['checkpoint_next_bottom'])
        self.checkpoint_bottom3.attach(create_sprite_checkpoint(self.assets['checkpoint_next_bottom']))

        # self.enemy_1 = create_sprite(V2(1900.0, 2100.0), 0, self.assets['enemy_ship'])
        # self.enemy_1.attach(create_sprite_locator(self.assets['enemy_ship'], 0.50))
        # self.enemy_2 = create_sprite(V2(1900.0, 2100.0), 0, self.assets['enemy_ship'])
        # self.enemy_2.attach(create_sprite_locator(self.assets['enemy_ship'], 0.50))
        # self.enemy_3 = create_sprite(V2(1900.0, 2100.0), 0, self.assets['enemy_ship'])
        # self.enemy_3.attach(create_sprite_locator(self.assets['enemy_ship'], 0.50))
        # self.enemy_4 = create_sprite(V2(1900.0, 2100.0), 0, self.assets['enemy_ship'])
        # self.enemy_4.attach(create_sprite_locator(self.assets['enemy_ship'], 0.50))

        # Create a turrent base for moon_plant_1 
        # 75 off to make it perfectly on top it seems
        # self.turret_base_entity_1 = create_sprite(V2(-715.0, -275.0), 0, self.assets['turret_base'])

        # Create a turrent base for moon_plant_1 
        # 16 off to make it perfectly on top it seems
        # self.turret_basic_cannon_1 = create_sprite(V2(-715.0, -275.0), 0, self.assets['turret_basic_cannon'])

        # Create a ship entity that we can control
        self.ship_entity = create_sprite(V2(200.0, 200.0), 0, self.assets['base_ship'], 0.25)
        self.ship_entity.attach(InputComponent())
        self.ship_entity.attach(EmitterBoostComponent(
            image=self.assets['energy_particle_cyan'],
            boost_image=self.assets['energy_particle_red'],
            batch=pyglet.graphics.Batch(),
            rate=0.1,
        ))


        self.flight_path_1 = Entity()


        points = [
            V2(110.0 - 70, 110.0 + 43),
            V2(220.0 - 70, 76.0 + 43),
            V2(225.0 - 70, -35.0 + 43),
            V2(130.0 - 70, -205.0 + 43),
            V2(-550.0 - 70, 0.0 + 43),
            V2(-861.0 - 70, -293.0 + 43),
            V2(-500.0, -133.0),
            V2(-600.0, 600.0),
            V2(-700.0, 1100.0),
            V2(50.0, 1400.0),
            V2(352.0, 1000.0),
            V2(50.0, 1340.0),
            V2(500.0, 1700.0),
            V2(1900.0, 2100.0),
        ]


        new_points = []
        for i, point in enumerate(points):
            if i < 3:
                new_points.append(point)
            else:
                new_points.append(new_points[-1] - new_points[-2] + new_points[-1])
                new_points.append(point)

        vertices = []
        path = []
        for i, p in enumerate(zip(new_points, new_points[1:], new_points[2:])):
            if i % 2 == 0:
                for i in range(32 + 1):
                    t = i / 32
                    x = (1 - t) * (1 - t) * p[0].x + 2 * (1 - t) * t * p[1].x + t * t * p[2].x
                    y = (1 - t) * (1 - t) * p[0].y + 2 * (1 - t) * t * p[1].y + t * t * p[2].y
                    vertices.append(x)
                    vertices.append(y)
                    path.append(V2(x, y))

        new_points_p = []
        for p in new_points:
            new_points_p.append(p.x)
            new_points_p.append(p.y)

        self.flight_path_1.attach(
            FlightPathComponent(
                path = path,
                vertices = pyglet.graphics.vertex_list(len(vertices) // 2,
                    ('v2f', vertices),
                    ('c4B', list(y for x, y in zip(range(len(vertices) // 2 * 4), cycle((255, 0, 0, 50))))),
                ),
                points = pyglet.graphics.vertex_list(len(new_points),
                    ('v2f', new_points_p),
                    ('c4B', list(y for x, y in zip(range(len(new_points) * 4), cycle((255, 0, 255, 50))))),
                )
            )
        )

        # self.enemy_1.attach(EnemyComponent(
        #     flight_path=self.flight_path_1.entity_id,
        #     offset=V2.from_degrees_and_length(random() * 360, random() * 50.0),
        #     speed=random() * 0.3 + 0.2,
        # ))

        # self.enemy_2.attach(EnemyComponent(
        #     flight_path=self.flight_path_1.entity_id,
        #     offset=V2.from_degrees_and_length(random() * 360, random() * 50.0),
        #     speed=random() * 0.3 + 0.2,
        # ))

        # self.enemy_3.attach(EnemyComponent(
        #     flight_path=self.flight_path_1.entity_id,
        #     offset=V2.from_degrees_and_length(random() * 360, random() * 50.0),
        #     speed=random() * 0.3 + 0.2,
        # ))

        # self.enemy_4.attach(EnemyComponent(
        #     flight_path=self.flight_path_1.entity_id,
        #     offset=V2.from_degrees_and_length(random() * 360, random() * 50.0),
        #     speed=random() * 0.3 + 0.2,
        # ))

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

