import pyglet

from .assets import ASSETS
from .common import *
from .components import (
    MenuComponent,
    UIVisualComponent,
    Visual,
)
from .ecs import *
from .vector import *
from .settings import settings


class MenuSystem(System):
    def setup(self):
        self.subscribe("DisplayMenu", self.handle_display_menu)
        self.subscribe("MenuSelection", self.handle_menu_selection)
        self.subscribe("MenuAccept", self.handle_menu_accept)
        self.create_main_menu()
        self.create_ship_menu()
        self.create_settings_menu()

    def handle_menu_selection(self, *, direction, **kwargs):
        for entity in Entity.with_component("menu"):
            menu = entity["menu"]
            if not menu.displayed:
                continue

            size = len(menu.option_labels)
            if direction == "up":
                menu.selected_option = (menu.selected_option - 1) % size
            elif direction == "down":
                menu.selected_option = (menu.selected_option + 1) % size
            return

    def handle_menu_accept(self, **kwargs):
        for entity in Entity.with_component("menu"):
            menu = entity["menu"]
            if not menu.displayed:
                continue
            option = menu.option_labels[menu.selected_option]
            callback = menu.option_callbacks[option]
            callback()
            return

    def play_game(self):
        print("Play Game selected")
        # Unlock physics
        settings.PHYSICS_FROZEN = False

        for menu_entity in Entity.with_component("menu"):
            menu = menu_entity["menu"]
            menu.displayed = False

        # Load the map
        System.dispatch(event="LoadMap", map_name="default")

    def change_ship(self):
        print("change ship")
        System.dispatch(event="DisplayMenu", menu_name="ship menu")

    def select_ship(self, ship_name):
        settings.selected_ship = ship_name
        entity = get_ship_entity()
        entity["game visual"].visuals[0].value.image = ASSETS[ship_name]
        System.dispatch(event="DisplayMenu", menu_name="main menu")

    def open_settings(self):
        System.dispatch(event="DisplayMenu", menu_name="settings menu")

    def open_main(self):
        System.dispatch(event="DisplayMenu", menu_name="main menu")

    def change_turning_style(self):
        settings.mouse_turning = not settings.mouse_turning
        for menu_entity in Entity.with_component("menu"):
            menu = menu_entity["menu"]
            if menu.menu_name == "settings menu":
                option_index = menu.selected_option
                style = "Turning Style: Mouse" if settings.mouse_turning else "Turning Style: A & D Keys"
                menu.option_labels[option_index] = style

    def change_camera_spring(self):
        settings.camera_spring = not settings.camera_spring
        for menu_entity in Entity.with_component("menu"):
            menu = menu_entity["menu"]
            if menu.menu_name == "settings menu":
                option_index = menu.selected_option
                spring = "Camera Spring: On" if settings.camera_spring else "Camera Spring: Off"
                menu.option_labels[option_index] = spring

    def create_settings_menu(self):
        options = {
            "Turning Style: A & D Keys": self.change_turning_style,
            "Turning Style: Mouse": self.change_turning_style,
            "Camera Spring: On": self.change_camera_spring,
            "Camera Spring: Off": self.change_camera_spring,
            "Back to Menu": self.open_main,
        }
        option_labels = [
            "Turning Style: Mouse" if settings.mouse_turning else "Turning Style: A & D Keys",
            "Camera Spring: On" if settings.camera_spring else "Camera Spring: Off",
            "Back to Menu",
        ]

        labels = []
        for option in option_labels:
            labels.append(
                pyglet.text.Label(
                    option,
                    font_size=36,
                    x=0,
                    y=0,
                    anchor_x="left",
                    anchor_y="center",
                )
            )

        visuals = [Visual(kind="menu options", z_sort=10, value=labels)]

        entity = Entity()
        entity.attach(
            MenuComponent(
                menu_name="settings menu",
                option_labels=option_labels,
                option_callbacks=options,
            )
        )
        entity.attach(
            UIVisualComponent(
                top=0.66,
                right=0.33,
                visuals=visuals,
            )
        )


    def create_main_menu(self):
        options = {
            "Play": self.play_game,
            "Change Ship": self.change_ship,
            "Settings": self.open_settings,
        }
        option_labels = [l for l in options]

        labels = []
        for option in option_labels:
            labels.append(
                pyglet.text.Label(
                    option,
                    font_size=36,
                    x=0,
                    y=0,
                    anchor_x="left",
                    anchor_y="center",
                )
            )

        visuals = [Visual(kind="menu options", z_sort=10, value=labels)]

        entity = Entity()
        entity.attach(
            MenuComponent(
                menu_name="main menu",
                option_labels=option_labels,
                option_callbacks=options,
            )
        )
        entity.attach(
            UIVisualComponent(
                top=0.66,
                right=0.33,
                visuals=visuals,
            )
        )

    def create_ship_menu(self):
        options = {
            "Avocado": (lambda: self.select_ship("Avocado")),
            "Martian Express": (lambda: self.select_ship("Martian Express")),
            "Sparrow": (lambda: self.select_ship("Sparrow")),
            "BMS-12": (lambda: self.select_ship("BMS-12")),
        }
        option_labels = [l for l in options]

        labels = []
        for option in option_labels:
            labels.append(
                pyglet.text.Label(
                    option,
                    font_size=36,
                    x=0,
                    y=0,
                    anchor_x="left",
                    anchor_y="center",
                )
            )

        visuals = [Visual(kind="menu options", z_sort=10, value=labels)]

        entity = Entity()
        entity.attach(
            MenuComponent(
                menu_name="ship menu",
                option_labels=option_labels,
                option_callbacks=options,
            )
        )
        entity.attach(
            UIVisualComponent(
                top=0.66,
                right=0.33,
                visuals=visuals,
            )
        )

    def handle_display_menu(self, *, menu_name, **kwargs):
        print(f"displaying menu {menu_name}")
        settings.PHYSICS_FROZEN = True

        # Move ship way off screen
        ship_entity = get_ship_entity()
        ship_physics = ship_entity["physics"]
        ship_physics.position = V2(-10000, -10000)

        # Move window camera to origin
        window = get_window()
        window.camera_position = V2(0, 0)

        for menu_entity in Entity.with_component("menu"):
            menu = menu_entity["menu"]
            if menu.menu_name == menu_name:
                menu.displayed = True
            else:
                menu.displayed = False

    def update(self):
        pass
