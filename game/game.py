import pygame
import os
from pygame.math import Vector2 as V2

# ECS Import
from . import ecs

# Entity Imports
from .ecs import Entity

# Component Imports
from .screen_component import ScreenComponent
from .surface_component import SurfaceComponent
from .position_component import PositionComponent
from .input_component import InputComponent

# System Imports
from .event_system import EventSystem
from .render_system import RenderSystem
from .physics_system import PhysicsSystem


# Global objects
ASSETS = {}
RESOLUTION = 900, 500


def create_sprite(position, rotate, surface, scale=1.0):
    sprite = Entity()
    sprite.attach(PositionComponent(position=position, rotate=rotate))
    sprite.attach(SurfaceComponent(surface=surface, scale=scale))
    return sprite


def load_image(asset_name):
    return pygame.image.load(os.path.join('assets', asset_name))


def run_game():

    # Initialize our systems in the order we want them to run
    # Events should come first, so we can react to input as 
    # quikli as possible
    event_system = EventSystem()

    # Physics system handles movement an collision
    physics_system = PhysicsSystem()

    # The render system draws things to the screen
    render_system = RenderSystem()

    # Initialize pygame
    pygame.init()

    # Load all of our assets
    # ASSETS['background'] = pygame.transform.scale(load_image('solar-system.jpg'), RESOLUTION)
    ASSETS['background'] = load_image('solar-system.jpg')
    ASSETS['base_ship'] = load_image('ship-base-256x256.png')
    ASSETS['red_planet'] = load_image('red-planet.png')
    ASSETS['red_planet_shield'] = load_image('red-planet-shield.png')
    ASSETS['moon'] = load_image('moon-128x128.png')
    ASSETS['turret_base'] = load_image('turret-basic-base-64x64.png')
    ASSETS['turret_basic_cannon'] = load_image('turret-basic-cannon-64x64.png')

    # Create a background entity
    screen_entity = Entity()
    screen=pygame.display.set_mode(RESOLUTION)
    screen_entity.attach(ScreenComponent(screen=screen, background=ASSETS['background']))

    # Create a home planet that will be set at a specific coordinate area
    red_planet_entity = create_sprite(V2(2048.0, 2048.0), 0, ASSETS['red_planet'])

    # Create a shield to go over the planet entity. This will need to be callable some other way for a power up and coordinate location
    red_planet_shield_entity = create_sprite(V2(2048.0, 2048.0), 0, ASSETS['red_planet_shield'])

    # we could probably create a def function to create these based on a series of coords
    # Create a moon for a specific location number 1
    moon_planet_entity_1 = create_sprite(V2(2650,1400), 0, ASSETS['moon'])

    # Create a moon for a specific location number 2
    moon_planet_entity_2 = create_sprite(V2(2400,600), 0, ASSETS['moon'])

    # Create a moon for a specific location number 3
    moon_planet_entity_3 = create_sprite(V2(3730,860), 0, ASSETS['moon'])

    # Create a turrent base for moon_plant_1 
    # 75 off to make it perfectly on top it seems
    turret_base_entity_1 = create_sprite(V2(2650,1325), 0, ASSETS['turret_base'])

    # Create a turrent base for moon_plant_1 
    # 16 off to make it perfectly on top it seems
    turret_basic_cannon_1 = create_sprite(V2(2650,1325), 0, ASSETS['turret_basic_cannon'])

    # Create a ship entity that we can control
    ship_entity = create_sprite(V2(2048.0, 1850.0), 0, ASSETS['base_ship'], 0.25)
    ship_entity.attach(InputComponent())

    # This is the game loop.  Yup, that's all of it.
    ecs.System.run()

