import os
import sys


import pyglet
# Has to be imported before pyglet.media is accessed
pyglet.options['audio'] = ('pulse', 'directsound', 'openal', 'silent')

from pyglet.window import key

# ECS Import
from . import ecs
from .settings import settings
from .assets import ASSETS
from .common import *
from .coordinates import *
from .ecs import *
from .vector import V2

# Component Imports
from .components import (
    WindowComponent,
    PhysicsComponent,
    InputComponent,
    Emitter,
    EmitterBoost,
    Visual,
    GameVisualComponent,
    UIVisualComponent,
    ShipComponent,
    CollisionComponent,
)

# System Imports
from .render_system import RenderSystem
from .cartography_system import CartographySystem
from .physics_system import PhysicsSystem
from .racing_system import RacingSystem
from .audio_system import AudioSystem
from .menu_system import MenuSystem


def load_image(asset_name, center=True, anchor_x=0, anchor_y=0):
    image = pyglet.image.load(os.path.join("assets", asset_name))
    if center:
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
    if anchor_x != 0:
        image.anchor_x = anchor_x
    if anchor_y != 0:
        image.anchor_y = anchor_y
    return image


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_assets()
        self.create_ship()
        self.create_fps_meter()

    def load_assets(self):
        # Ship Images
        ASSETS["Avocado"] = load_image("ship-base-256x256.png")
        ASSETS["Martian Express"] = load_image("ship-speed-256x256.png")
        ASSETS["Sparrow"] = load_image("ship-speed-weapon-256x256.png")
        ASSETS["BMS-12"] = load_image("ship-weapon-256x256.png")

        ASSETS["asteroid_large"] = load_image("large-asteroid-512x512.png")
        ASSETS["asteroid_medium"] = load_image("medium-asteroid-256x256.png")
        ASSETS["asteroid_small"] = load_image("asteroid-small-128x128.png")
        ASSETS["base_flare"] = load_image("base-flare-32x32.png")
        ASSETS["black_hole"] = load_image("black-hole-1024x1024.png")
        ASSETS["boost_powerup"] = load_image("boost-powerup-256x256.png")
        ASSETS["boost_tick_blue"] = load_image("boost-tick-blue-48x48.png")
        ASSETS["boost_tick_red"] = load_image("boost-tick-red-48x48.png")
        ASSETS["boost_tick_yellow"] = load_image("boost-tick-yellow-48x48.png")
        ASSETS["boost_ui_base"] = load_image("boost-ui-base-288x64.png")
        ASSETS["checkpoint_arrow"] = load_image(
            "checkpoint-arrow-128x128.png", anchor_x=128, anchor_y=64
        )
        ASSETS["checkpoint_bottom"] = load_image("checkpoint-bottom-256x256.png")
        ASSETS["checkpoint_finish_bottom"] = load_image(
            "checkpoint-finish-bottom-256x256.png"
        )
        ASSETS["checkpoint_finish_top"] = load_image(
            "checkpoint-finish-top-256x256.png"
        )
        ASSETS["checkpoint_next_bottom"] = load_image(
            "checkpoint-next-bottom-256x256.png"
        )
        ASSETS["checkpoint_next_top"] = load_image("checkpoint-next-top-256x256.png")
        ASSETS["checkpoint_passed_bottom"] = load_image(
            "checkpoint-passed-bottom-256x256.png"
        )
        ASSETS["checkpoint_passed_top"] = load_image(
            "checkpoint-passed-top-256x256.png"
        )
        ASSETS["checkpoint_top"] = load_image("checkpoint-top-256x256.png")
        ASSETS["closer_stars"] = load_image("closer-stars-2048x2048.png", center=False)
        ASSETS["dwarf_gas_planet"] = load_image("dwarf-gas-planet-512x512.png")
        ASSETS["earth"] = load_image("earth-1024x1024.png")
        ASSETS["energy_particle_cyan"] = load_image("energy-particle-cyan-64x64.png")
        ASSETS["energy_particle_red"] = load_image("energy-particle-red-64x64.png")
        ASSETS["gas_giant"] = load_image("gas-giant-1024x1024.png")
        ASSETS["medium_gas_planet"] = load_image("medium-gas-planet-512x512.png")
        ASSETS["moon"] = load_image("moon-128x128.png")
        ASSETS["nebula"] = load_image("nebula-2048x2048.png", center=False)
        ASSETS["particle_flare"] = load_image("particle-flare-32x32.png")
        ASSETS["red_planet"] = load_image("red-planet-512x512.png")
        ASSETS["red_planet_shield"] = load_image("red-planet-shield-512x512.png")
        ASSETS["satellite"] = load_image("satellite-256x256.png")
        ASSETS["slowdown"] = load_image("slowdown-256x256.png")
        ASSETS["star_field"] = load_image("starfield-2048x2048.png", center=False)
        ASSETS["3_2_1"] = pyglet.media.load(os.path.join("assets", "3_2_1.wav"), streaming=False)
        ASSETS["go"] = pyglet.media.load(os.path.join("assets", "go.wav"), streaming=False)
        ASSETS["collision"] = pyglet.media.load(os.path.join("assets", "collision.wav"), streaming=False)
        ASSETS["map_win"] = pyglet.media.load(os.path.join("assets", "fanfare_low.wav"), streaming=False)
        ASSETS["cp_complete"] = pyglet.media.load(os.path.join("assets", "cp_complete.wav"), streaming=False)
        ASSETS["slowdown_sound"] = pyglet.media.load(os.path.join("assets", "slowdown.wav"), streaming=False)
        ASSETS["boost_powerup_sound"] = pyglet.media.load(os.path.join("assets", "boost_powerup.wav"), streaming=False)
        ASSETS["thrust_sound"] = pyglet.media.load(os.path.join("assets", "regular_thrust.wav"), streaming=False)
        ASSETS["boost_sound"] = pyglet.media.load(os.path.join("assets", "booster_thrust_16.wav"), streaming=False)
        ASSETS["large_red_planet"] = load_image("red-planet-4096x4096.png")
        ASSETS["tutorial_map"] = load_image("map-tutorial_map-256x256.png")
        ASSETS["getting_started"] = load_image("map-getting_started-256x256.png")
        ASSETS["random_map"] = load_image("map-random_map-256x256.png")
        ASSETS["slalom_map"] = load_image("map-slalom_map-256x256.png")
        ASSETS["speedy_map"] = load_image("map-speedy_map-256x256.png")
        ASSETS["final_map"] = load_image("map-final_map-256x256.png")
        Entity().attach(InputComponent())

    def create_fps_meter(self):
        def get_avg_fps(over_ticks):
            ticks = list(0 for _ in range(over_ticks))
            tick = 0

            def inner():
                nonlocal ticks
                nonlocal tick
                if ecs.DELTA_TIME > 0:
                    FPS = 1.0 / ecs.DELTA_TIME
                else:
                    FPS = 60
                ticks[tick] = int(FPS)
                tick = (tick + 1) % over_ticks
                avg_FPS = int(sum(ticks) / over_ticks)
                min_FPS = int(min(ticks))
                max_FPS = int(max(ticks))
                return f"FPS: {avg_FPS} [{min_FPS}, {max_FPS}]"

            return inner

        if False:
            fps_entity = Entity()
            label = pyglet.text.Label(
                "FPS", font_size=24, x=0, y=0, anchor_x="left", anchor_y="top"
            )
            fps_entity.attach(
                UIVisualComponent(
                    top=0.985,
                    right=0.0,
                    visuals=[
                        Visual(
                            kind="real time label",
                            z_sort=1.0,
                            value={
                                "fn": get_avg_fps(10),
                                "label": label,
                            },
                        )
                    ],
                )
            )

    def create_ship(self):
        # Entity Components
        entity = Entity()
        physics = PhysicsComponent(position=V2(0, 0), rotation=0, static=False)
        ship = ShipComponent()

        # Game Visuals
        ship_name = settings.selected_ship

        set_ship_stats(ship_name, ship, physics)

        sprite = pyglet.sprite.Sprite(ASSETS[ship_name], x=0, y=0, subpixel=True)
        sprite.scale = 0.25
        emitter = EmitterBoost(
            image=ASSETS["energy_particle_cyan"],
            boost_image=ASSETS["energy_particle_red"],
            batch=pyglet.graphics.Batch(),
            rate=0.1,
        )
        game_visuals = [
            Visual(kind="sprite", z_sort=-10.0, value=sprite),
            Visual(kind="emitter", z_sort=-11.0, value=emitter),
        ]

        # UI Visuals
        boost_visual = {
            "base": pyglet.sprite.Sprite(ASSETS["boost_ui_base"]),
            "ticks": [
                pyglet.sprite.Sprite(ASSETS["boost_tick_red"]),
                pyglet.sprite.Sprite(ASSETS["boost_tick_yellow"]),
                pyglet.sprite.Sprite(ASSETS["boost_tick_yellow"]),
                pyglet.sprite.Sprite(ASSETS["boost_tick_yellow"]),
                pyglet.sprite.Sprite(ASSETS["boost_tick_yellow"]),
                pyglet.sprite.Sprite(ASSETS["boost_tick_blue"]),
                pyglet.sprite.Sprite(ASSETS["boost_tick_blue"]),
                pyglet.sprite.Sprite(ASSETS["boost_tick_blue"]),
                pyglet.sprite.Sprite(ASSETS["boost_tick_blue"]),
                pyglet.sprite.Sprite(ASSETS["boost_tick_blue"]),
            ],
        }
        ui_visuals = [
            Visual(kind="boost", z_sort=0.0, value=boost_visual),
        ]

        entity.attach(physics)
        entity.attach(ship)
        entity.attach(CollisionComponent(circle_radius=24))
        entity.attach(GameVisualComponent(visuals=game_visuals))
        entity.attach(UIVisualComponent(visuals=ui_visuals))

    def on_key_press(self, symbol, modifiers):
        inputs = get_inputs()
        if symbol == key.W:
            inputs.w = True
            System.dispatch(event="MenuSelection", direction="up")
        elif symbol == key.A:
            inputs.a = True
        elif symbol == key.S:
            inputs.s = True
            System.dispatch(event="MenuSelection", direction="down")
        elif symbol == key.D:
            inputs.d = True
        elif symbol == key.LSHIFT:
            inputs.boost = True
        elif symbol == key.R:
            System.dispatch(event="Respawn")
        elif symbol == key.UP:
            System.dispatch(event="MenuSelection", direction="up")
        elif symbol == key.DOWN:
            System.dispatch(event="MenuSelection", direction="down")
        elif symbol == key.RETURN:
            System.dispatch(event="MenuAccept")
        elif symbol == key.SPACE:
            System.dispatch(event="MenuAccept")
        elif symbol == key.BACKSPACE:
            System.dispatch(event="Pause")

    def on_key_release(self, symbol, modifiers):
        inputs = get_inputs()
        if symbol == key.W:
            inputs.w = False
        elif symbol == key.A:
            inputs.a = False
        elif symbol == key.S:
            inputs.s = False
        elif symbol == key.D:
            inputs.d = False
        elif symbol == key.LSHIFT:
            inputs.boost = False

    def on_mouse_motion(self, x, y, dx, dy):
        window = get_window()
        camera = window.camera_position
        width, height = window.window.width, window.window.height
        w_x, w_y = screen_to_world(
            x, y, width, height, camera.x, camera.y, window.camera_zoom
        )
        mouse_position = V2(w_x, w_y)
        entity = get_ship_entity()
        ship_physics = entity["physics"]
        ship_position = ship_physics.position

        if settings.MOUSE_TURNING:
            ship_physics.rotation = (
                mouse_position - ship_physics.position
            ).degrees - 90

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        window = get_window()
        if scroll_y > 0:
            window.camera_zoom /= 1.1
        else:
            window.camera_zoom *= 1.1


def run_game():

    # Create a Window entity
    window_entity = Entity()
    window = GameWindow(1280, 720, resizable=True)
    window_entity.attach(
        WindowComponent(
            window=window,
            background_layers=[
                pyglet.sprite.Sprite(ASSETS["star_field"], x=0, y=0),
                pyglet.sprite.Sprite(ASSETS["closer_stars"], x=0, y=0),
                pyglet.sprite.Sprite(ASSETS["nebula"], x=0, y=0),
            ],
        )
    )

    # Handle all of our menus
    MenuSystem()

    # Make, load, and manage maps
    CartographySystem()

    # Physics system handles movement an collision
    PhysicsSystem()

    # System for managing a race
    RacingSystem()

    # System for managing a race
    AudioSystem()

    # The render system draws things to the Window
    RenderSystem()

    System.dispatch(event="DisplayMenu", menu_name="main menu")

    def update(dt, *args, **kwargs):
        ecs.DELTA_TIME = dt
        window.clear()
        System.update_all()

    pyglet.clock.schedule(update, 1 / 60.0)
    pyglet.app.run()
