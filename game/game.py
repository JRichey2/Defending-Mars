# ECS Import
from . import ecs

# Entity Imports
from .ecs import Entity

# Component Imports
from .echo_component import EchoComponent

# System Imports
from .echo_system import EchoSystem
from .event_system import EventSystem
from .render_system import RenderSystem


def run_game():

    # Initialize our systems in the order we want them to run
    # Events should come first, so we can react to input as 
    # quikli as possible
    event_system = EventSystem()

    # The echo system can be used for debugging
    echo_system = EchoSystem()
    # The echo system is interested in responding to Key Press events
    echo_system.subscribe('Key Press')

    # The render system draws things to the screen
    render_system = RenderSystem()

    # This entity is just for testing.
    # When we have actual game entities, we'll initialize those instead.
    test_entity = Entity()
    test_entity.attach(EchoComponent())

    # This is the game loop.  Yup, that's all of it.
    while True:
        ecs.System.update_all()
