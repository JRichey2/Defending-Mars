import pyglet
import os
from itertools import cycle

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
    EmitterComponent,
    FlightPathComponent,
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
        self.assets['red_planet'] = load_image('red-planet.png')
        self.assets['red_planet_shield'] = load_image('red-planet-shield.png')
        self.assets['moon'] = load_image('moon-128x128.png')
        self.assets['turret_base'] = load_image('turret-basic-base-64x64.png')
        self.assets['turret_basic_cannon'] = load_image('turret-basic-cannon-64x64.png')
        self.assets['energy_particle_cyan'] = load_image('energy-particle-cyan-64x64.png')

        # Create a home planet that will be set at a specific coordinate area
        self.red_planet_entity = create_sprite(V2(0.0, 0.0), 0, self.assets['red_planet'])

        # Create a shield to go over the planet entity. This will need to be callable some other way for a power up and coordinate location
        self.red_planet_shield_entity = create_sprite(V2(0.0, 0.0), 0, self.assets['red_planet_shield'])

        # we could probably create a def function to create these based on a series of coords
        # Create a moon for a specific location number 1
        self.moon_planet_entity_1 = create_sprite(V2(500.0,500.0), 0, self.assets['moon'])

        # Create a moon for a specific location number 2
        self.moon_planet_entity_2 = create_sprite(V2(-500.0,-500.0), 0, self.assets['moon'])

        # Create a moon for a specific location number 3
        self.moon_planet_entity_3 = create_sprite(V2(1300.0,860.0), 0, self.assets['moon'])

        # Create a turrent base for moon_plant_1 
        # 75 off to make it perfectly on top it seems
        self.turret_base_entity_1 = create_sprite(V2(500.0,575.0), 0, self.assets['turret_base'])

        # Create a turrent base for moon_plant_1 
        # 16 off to make it perfectly on top it seems
        self.turret_basic_cannon_1 = create_sprite(V2(500.0,575.0), 0, self.assets['turret_basic_cannon'])

        # Create a ship entity that we can control
        self.ship_entity = create_sprite(V2(200.0, 200.0), 0, self.assets['base_ship'], 0.25)
        self.ship_entity.attach(InputComponent())
        self.ship_entity.attach(EmitterComponent(
            image=self.assets['energy_particle_cyan'],
            batch=pyglet.graphics.Batch(),
            rate=0.1,
        ))

        self.flight_path_1 = Entity()


        points = [
            V2(100.0, 100.0),
            V2(110.0, 110.0),
            V2(300.0, 100.0),
            V2(300.0, -300.0),
            V2(-500.0, -300.0),
            V2(-2000.0, 1000.0),
        ]


        new_points = []
        for i, point in enumerate(points):
            if i == 0:
                new_points.append(point)
            elif i == 1:
                new_points.append((point - new_points[0]) * 0.5)
                new_points.append(point)
            else:
                new_points.append(new_points[-1] - new_points[-2] + new_points[-1])
                new_points.append(point)

        vertices = []
        for i, p in enumerate(zip(new_points, new_points[1:], new_points[2:])):
            if i % 2 == 0:
                for i in range(16 + 1):
                    t = i / 16
                    x = (1 - t) * (1 - t) * p[0].x + 2 * (1 - t) * t * p[1].x + t * t * p[2].x
                    y = (1 - t) * (1 - t) * p[0].y + 2 * (1 - t) * t * p[1].y + t * t * p[2].y
                    vertices.append(x)
                    vertices.append(y)

        self.flight_path_1.attach(
            FlightPathComponent(
                vertices = pyglet.graphics.vertex_list(len(vertices) // 2,
                    ('v2f', vertices),
                    ('c4B', list(y for x, y in zip(range(len(vertices) // 2 * 4), cycle((255, 0, 0, 50))))),
                )
            )
        )

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

