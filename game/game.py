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


def create_sprite(x, y, surface):
    sprite = Entity()
    sprite.attach(PositionComponent(x=x, y=y))
    sprite.attach(SurfaceComponent(surface=surface))
    return sprite

def run_game():

    # Initialize our systems in the order we want them to run
    # Events should come first, so we can react to input as 
    # quikli as possible
    event_system = EventSystem()

    physics_system = PhysicsSystem()

    # The render system draws things to the screen
    render_system = RenderSystem()

    pygame.init()
    screen_entity = Entity()
    screen=pygame.display.set_mode((900, 500))
    background = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'space.png')), (900, 500))

    screen_entity.attach(ScreenComponent(screen=screen, background=background))

    ship_entity = create_sprite(450, 250, pygame.image.load(os.path.join('assets', 'spaceship_yellow.png')))
    ship_entity.attach(InputComponent())
    ship_entity2 = create_sprite(100, 50, pygame.image.load(os.path.join('assets', 'spaceship_red.png')))

    # This is the game loop.  Yup, that's all of it.
    while True:
        ecs.System.update_all()

