import json
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



SHIPS = {
    "Avocado": (
        'A well-rounded fruit\n'
        'Top Speed: Average\n'
        'Acceleration: Average\n'
        'Boost Power: Average'
    ),
    "Martian Express": (
        'Great news everybody!\n'
        'Top Speed: Best\n'
        'Acceleration: Poor\n'
        'Boost Power: Poor'
    ),
    "Sparrow": (
        "Won't steal your fries\n"
        'Top Speed: Poor\n'
        'Acceleration: Poor\n'
        'Boost Power: Best'
    ),
    "BMS-12": (
        "Nanananananananana\n"
        'Top Speed: Poor\n'
        'Acceleration: Best\n'
        'Boost Power: Poor'
    ),
}


MAPS = {
    "Tutorial Map": (
        'tutorial_map',
        'Learn the game',
    ),
    "Getting Started Map": (
        'getting_started',
        'A simple map',
    ),
    "Take a Tour Map": (
        'random_map',
        'A scenic tour',
    ),
    "Slalom Map": (
        'slalom_map',
        'A weaving path through obstacles',
    ),
    "Speed Map": (
        'speedy_map',
        'A map designed to get high speeds',
    ),
    "The Red Planet Map": (
        'final_map',
        'Around the red planet in 34 checkpoints',
    ),
}


class MenuSystem(System):
    def setup(self):
        self.subscribe("DisplayMenu", self.handle_display_menu)
        self.subscribe("MenuSelection", self.handle_menu_selection)
        self.subscribe("MenuAccept", self.handle_menu_accept)
        self.subscribe("Pause", self.handle_pause)
        self.subscribe("RaceComplete", self.handle_race_complete)
        self.create_main_menu()
        self.create_ship_menu()
        self.create_settings_menu()
        self.create_map_menu()
        self.create_in_game_menu()
        self.create_finish_menu()


    def handle_pause(self):
        if not map_is_active():
            return
        if settings.physics_frozen:
            self.back_to_race()
        else:
            settings.physics_frozen = True
            System.dispatch(event="DisplayMenu", menu_name="in-game menu")

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

            if menu.menu_name == 'ship menu':
                ship = menu.option_labels[menu.selected_option]
                description = SHIPS[ship]
                visuals = entity['ui visual'].visuals
                ship_sprite = visuals[1].value
                ship_sprite.image = ASSETS[ship]
                ship_label = visuals[2].value
                ship_label.text = description

            elif menu.menu_name == 'map menu':
                map_title = menu.option_labels[menu.selected_option]
                map_name, map_description = MAPS.get(map_title, (None, None))
                visuals = entity['ui visual'].visuals
                map_sprite = visuals[1].value
                map_label = visuals[2].value
                if map_name:
                    map_sprite.image = ASSETS[map_name]
                    map_sprite.visible = True
                    map_label.text = map_description
                    map_label.visible = True
                else:
                    map_sprite.visible = False
                    map_label.visible = False

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

    def play_game(self, map_name):
        # Unlock physics
        settings.physics_frozen = False

        for menu_entity in Entity.with_component("menu"):
            menu = menu_entity["menu"]
            menu.displayed = False

        # Load the map
        System.dispatch(event="LoadMap", map_name=map_name, mode="racing")

    def change_ship(self):
        System.dispatch(event="DisplayMenu", menu_name="ship menu")

    def select_ship(self, ship_name):
        settings.selected_ship = ship_name
        entity = get_ship_entity()
        entity["game visual"].visuals[0].value.image = ASSETS[ship_name]

        set_ship_stats(ship_name, entity['ship'], entity['physics'])

        System.dispatch(event="DisplayMenu", menu_name="main menu")

    def open_settings(self):
        System.dispatch(event="DisplayMenu", menu_name="settings menu")

    def open_main(self):
        map_entity = get_active_map_entity()
        if map_entity:
            System.dispatch(event="ExitMap", map_entity_id=map_entity.entity_id)
        System.dispatch(event="DisplayMenu", menu_name="main menu")

    def open_map_menu(self):
        System.dispatch(event="DisplayMenu", menu_name="map menu")

    def handle_race_complete(self, *, map_name, **kwargs):
        if not map_is_active():
            return
        settings.physics_frozen = True

        for menu_entity in Entity.with_component("menu"):
            menu = menu_entity["menu"]
            if menu.menu_name == 'finish menu':
                menu.displayed = True
                break

        map_entity = get_active_map_entity()
        map_ = map_entity['map']

        ct = map_.race_end_time - map_.race_start_time

        with open(os.path.join("records", "pb_times.json"), "r") as f:
            records = json.loads(f.read())
        pb = records.get(map_.map_name)
        if pb is None:
            pb = ct
        pb = int(pb * 100) / 100
        ct = int(ct * 100) / 100

        label = menu_entity['ui visual'].visuals[2].value
        label.text = f'Finish Time: {ct:.2f}s\nPersonal Best: {pb:.2f}s'

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

    def restart(self):
        settings.physics_frozen = False

        for menu_entity in Entity.with_component("menu"):
            menu = menu_entity["menu"]
            menu.displayed = False

        map_entity = get_active_map_entity()
        if map_entity:
            map_ = map_entity['map']
            System.dispatch(event="LoadMap", map_name=map_.map_name, mode=map_.mode)

    def back_to_race(self):
        settings.physics_frozen = False
        for menu_entity in Entity.with_component("menu"):
            menu = menu_entity["menu"]
            menu.displayed = False


    def create_finish_menu(self):
        options = {
            "Improve": self.restart,
            "Back to Menu": self.open_main,
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

        visuals = [
            Visual(kind="menu options", z_sort=10, value=labels),
            Visual(kind="menu sprite", z_sort=9, value=pyglet.sprite.Sprite(ASSETS[settings.selected_ship])),
            Visual(kind="menu description", z_sort = 10, value=pyglet.text.Label(
                'temp',
                align="center",
                multiline=True,
                font_size=24,
                width=400,
                anchor_x="center",
                anchor_y="top",
            ))
        ]

        entity = Entity()
        entity.attach(
            MenuComponent(
                menu_name="finish menu",
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

    def create_in_game_menu(self):
        options = {
            "Back to Race": self.back_to_race,
            "Restart": self.restart,
            "Exit to Menu": self.open_main,
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
                menu_name="in-game menu",
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

    def create_map_menu(self):
        options = {
            "Tutorial Map": (lambda: self.play_game('tutorial_map')),
            "Getting Started Map": (lambda: self.play_game('default')),
            "Take a Tour Map": (lambda: self.play_game('random_map')),
            "Slalom Map": (lambda: self.play_game('slalom_map')),
            "Speed Map": (lambda: self.play_game('speedy_map')),
            "The Red Planet Map": (lambda: self.play_game('final_map')),
            #"WIP Map": (lambda: self.play_game('wip')),
            "Back to Menu": self.open_main,
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

        visuals = [
            Visual(kind="menu options", z_sort=10, value=labels),
            Visual(kind="menu sprite", z_sort=9, value=pyglet.sprite.Sprite(ASSETS['tutorial_map'])),
            Visual(kind="menu description", z_sort = 10, value=pyglet.text.Label(
                'Tutorial Map',
                align="center",
                multiline=True,
                font_size=24,
                width=400,
                anchor_x="center",
                anchor_y="top",
            ))
        ]


        entity = Entity()
        entity.attach(
            MenuComponent(
                menu_name="map menu",
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
            "Play": self.open_map_menu,
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

        ship_description = SHIPS['Avocado']

        visuals = [
            Visual(kind="menu options", z_sort=10, value=labels),
            Visual(kind="menu sprite", z_sort=9, value=pyglet.sprite.Sprite(ASSETS['Avocado'])),
            Visual(kind="menu description", z_sort = 10, value=pyglet.text.Label(
                ship_description,
                align="center",
                multiline=True,
                font_size=24,
                width=400,
                anchor_x="center",
                anchor_y="top",
            ))
        ]

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
        settings.PHYSICS_FROZEN = True

        if menu_name != 'in-game menu':
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
