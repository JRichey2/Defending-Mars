import pyglet
import os

# ECS Import
from . import ecs
from .assets import ASSETS
from .ecs import Entity, Event, field
from .vector import V2
from .events import (
    MapEvent,
    KeyEvent,
    MouseMotionEvent,
    MouseButtonEvent,
    MouseScrollEvent,
)


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
from .timing_system import TimingSystem


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


class DefendingMarsWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_assets()
        self.create_ship()
        ecs.System.inject(MapEvent(kind='LoadMap', map_name='default'))

    def load_assets(self):
        ASSETS['star_field'] = load_image('starfield-2048x2048.png', center=False)
        ASSETS['closer_stars'] = load_image('closer-stars-2048x2048.png', center=False)
        ASSETS['nebula'] = load_image('nebula-2048x2048.png', center=False)
        ASSETS['base_ship'] = load_image('ship-base-256x256.png')
        ASSETS['enemy_ship'] = load_image('ship-speed-64x64.png')
        ASSETS['red_planet'] = load_image('red-planet-512x512.png')
        ASSETS['red_planet_shield'] = load_image('red-planet-shield-512x512.png')
        ASSETS['moon'] = load_image('moon-128x128.png')
        ASSETS['earth'] = load_image('earth-1024x1024.png')
        ASSETS['energy_particle_cyan'] = load_image('energy-particle-cyan-64x64.png')
        ASSETS['energy_particle_red'] = load_image('energy-particle-red-64x64.png')
        ASSETS['particle_flare'] = load_image('particle-flare-32x32.png')
        ASSETS['boost_ui_base'] = load_image('boost-ui-base-288x64.png')
        ASSETS['boost_tick_red'] = load_image('boost-tick-red-48x48.png')
        ASSETS['boost_tick_blue'] = load_image('boost-tick-blue-48x48.png')
        ASSETS['boost_tick_yellow'] = load_image('boost-tick-yellow-48x48.png')
        ASSETS['checkpoint_arrow'] = load_image('checkpoint-arrow-128x128.png', anchor_x=128, anchor_y=64)
        ASSETS['checkpoint_top'] = load_image('checkpoint-top-256x256.png')
        ASSETS['checkpoint_bottom'] = load_image('checkpoint-bottom-256x256.png')
        ASSETS['checkpoint_next_top'] = load_image('checkpoint-next-top-256x256.png')
        ASSETS['checkpoint_next_bottom'] = load_image('checkpoint-next-bottom-256x256.png')
        ASSETS['checkpoint_finish_top'] = load_image('checkpoint-finish-top-256x256.png')
        ASSETS['checkpoint_finish_bottom'] = load_image('checkpoint-finish-bottom-256x256.png')
        ASSETS['checkpoint_passed_top'] = load_image('checkpoint-passed-top-256x256.png')
        ASSETS['checkpoint_passed_bottom'] = load_image('checkpoint-passed-bottom-256x256.png')

    def create_ship(self):
        # Entity Components
        entity = Entity()
        entity.attach(PhysicsComponent(position=V2(0, 0), rotation=0))
        entity.attach(InputComponent())
        entity.attach(BoostComponent())
        entity.attach(CollisionComponent(circle_radius=24))

        # Game Visuals
        sprite=pyglet.sprite.Sprite(ASSETS['base_ship'], x=0, y=0, subpixel=True)
        sprite.scale = 0.25
        emitter = EmitterBoost(
            image=ASSETS['energy_particle_cyan'],
            boost_image=ASSETS['energy_particle_red'],
            batch=pyglet.graphics.Batch(),
            rate=0.1,
        )
        game_visuals = [
            Visual(kind="sprite", z_sort=-10.0, value=sprite),
            Visual(kind="emitter", z_sort=-11.0, value=emitter),
        ]
        entity.attach(GameVisualComponent(visuals=game_visuals))

        # UI Visuals
        boost_visual = {
            'base': pyglet.sprite.Sprite(ASSETS['boost_ui_base']),
            'ticks': [
                pyglet.sprite.Sprite(ASSETS['boost_tick_red']),
                pyglet.sprite.Sprite(ASSETS['boost_tick_yellow']),
                pyglet.sprite.Sprite(ASSETS['boost_tick_yellow']),
                pyglet.sprite.Sprite(ASSETS['boost_tick_yellow']),
                pyglet.sprite.Sprite(ASSETS['boost_tick_yellow']),
                pyglet.sprite.Sprite(ASSETS['boost_tick_blue']),
                pyglet.sprite.Sprite(ASSETS['boost_tick_blue']),
                pyglet.sprite.Sprite(ASSETS['boost_tick_blue']),
                pyglet.sprite.Sprite(ASSETS['boost_tick_blue']),
                pyglet.sprite.Sprite(ASSETS['boost_tick_blue']),
            ]
        }
        ui_visuals = [
            Visual(kind='boost', z_sort=0.0, value=boost_visual),
        ]
        entity.attach(UIVisualComponent(visuals=ui_visuals))

    def on_key_press(self, symbol, modifiers):
        ecs.System.inject(KeyEvent(kind='Key', key_symbol=symbol, pressed=True))

    def on_key_release(self, symbol, modifiers):
        ecs.System.inject(KeyEvent(kind='Key', key_symbol=symbol, pressed=False))

    def on_mouse_motion(self, x, y, dx, dy):
        ecs.System.inject(MouseMotionEvent(kind='MouseMotion', x=x, y=y, dx=dx, dy=dy))

    def on_mouse_press(self, x, y, button, modifiers):
        ecs.System.inject(MouseButtonEvent(kind='MouseClick', x=x, y=y, button=button, pressed=True))

    def on_mouse_release(self, x, y, button, modifiers):
        ecs.System.inject(MouseButtonEvent(kind='MouseRelease', x=x, y=y, button=button, pressed=False))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y ):
        ecs.System.inject(MouseScrollEvent(kind='MouseScroll', x=x, y=y, scroll_x=scroll_x, scroll_y=scroll_y ))

    def on_close(self):
        ecs.System.inject(Event(kind='Quit'))


def run_game():

    # Initialize our systems in the order we want them to run
    # Events should come first, so we can react to input as 
    # quikli as possible
    EventSystem()

    # Temporary for us to create maps with
    MappingSystem()

    # Physics system handles movement an collision
    PhysicsSystem()

    # Updates checkpoints
    CheckpointSystem()

    # Timing System to handle turning on and off movement/gravity/ freezing things
    TimingSystem()

    # The render system draws things to the Window
    RenderSystem()

    # Create a Window entity
    window_entity = Entity()
    window=DefendingMarsWindow(1280, 720, resizable=True)
    window_entity.attach(WindowComponent(
        window=window,
        background_layers = [
            pyglet.sprite.Sprite(ASSETS['star_field'], x=0, y=0),
            pyglet.sprite.Sprite(ASSETS['closer_stars'], x=0, y=0),
            pyglet.sprite.Sprite(ASSETS['nebula'], x=0, y=0),
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

