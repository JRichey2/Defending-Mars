import pygame
import os

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


def create_sprite(x, y, surface):
    sprite = Entity()
    sprite.attach(PositionComponent(x=x, y=y))
    sprite.attach(SurfaceComponent(surface=surface))
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
    ASSETS['background'] = pygame.transform.scale(load_image('space.png'), RESOLUTION)
    ASSETS['spaceship_yellow'] = load_image('spaceship_yellow.png')
    ASSETS['spaceship_red'] = load_image('spaceship_red.png')

    # Create a background entity
    screen_entity = Entity()
    screen=pygame.display.set_mode(RESOLUTION)
    screen_entity.attach(ScreenComponent(screen=screen, background=ASSETS['background']))

    # Create a ship entity that we can control
    ship_entity = create_sprite(450, 250, ASSETS['spaceship_yellow'])
    ship_entity.attach(InputComponent())

    # Create a second ship entity that we cannot control
    ship_entity2 = create_sprite(100, 50, ASSETS['spaceship_red'])

    # This is the game loop.  Yup, that's all of it.
    ecs.System.run()

