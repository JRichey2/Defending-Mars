import pyglet
import os

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
    image = pyglet.resource.image(os.path.join('assets', asset_name))
    if center:
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
    return image


class KeyEvent(Event):
    key_symbol = field(mandatory=True)
    pressed = field(type=bool, mandatory=True)


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

    def on_key_press(self, symbol, modifiers):
        ecs.System.inject(KeyEvent(kind='Key', key_symbol=symbol, pressed=True))

    def on_key_release(self, symbol, modifiers):
        ecs.System.inject(KeyEvent(kind='Key', key_symbol=symbol, pressed=False))

    def on_close(self):
        ecs.System.inject(Event(kind='Quit'))


def run_game():

    # Initialize our systems in the order we want them to run
    # Events should come first, so we can react to input as 
    # quikli as possible
    event_system = EventSystem()
    event_system.subscribe('Key')
    event_system.subscribe('Quit')

    # Physics system handles movement an collision
    physics_system = PhysicsSystem()

    # The render system draws things to the Window
    render_system = RenderSystem()

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

    pyglet.clock.schedule(update, 1/60.0)
    pyglet.app.run()

