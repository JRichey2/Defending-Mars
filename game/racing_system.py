import json
import os
import pyglet
import time

from itertools import cycle

from .settings import settings
from .assets import ASSETS
from .common import *
from .components import (
    PhysicsComponent,
    GameVisualComponent,
    UIVisualComponent,
    CountdownComponent,
    Visual,
    FlightPathComponent,
)
from .ecs import *
from .vector import *

from pyglet import clock


class RacingSystem(System):
    def setup(self):
        self.subscribe("MapLoaded", self.handle_map_loaded)
        self.subscribe("RaceStart", self.handle_race_start)
        self.subscribe("RaceComplete", self.handle_race_complete)

    def handle_map_loaded(self, *, map_entity_id, **kwargs):
        ship_entity = get_ship_entity()

        # Update the map component that was loaded to know about the countdown label
        map_entity = Entity.find(map_entity_id)
        map_ = map_entity["map"]

        if map_.mode != "racing":
            # Unfreeze the ship
            ship_entity["physics"].static = False
            return

        ship_entity["physics"].static = True

        def get_avg_speed(over_ticks):
            nonlocal ship_entity
            ticks = list(0 for _ in range(over_ticks))
            tick = 0
            physics = ship_entity["physics"]

            def inner():
                nonlocal ticks
                nonlocal tick
                ticks[tick] = 350 * ship_entity["physics"].velocity.length
                tick = (tick + 1) % over_ticks
                avg_speed = int(sum(ticks) / over_ticks)
                return f"{avg_speed} km/s"

            return inner

        speedometer_entity = Entity()
        label = pyglet.text.Label(
            "SPEED", font_size=36, x=0, y=0, anchor_x="center", anchor_y="bottom"
        )
        speedometer_entity.attach(
            UIVisualComponent(
                top=0.015,
                right=0.5,
                visuals=[
                    Visual(
                        kind="real time label",
                        z_sort=1.0,
                        value={
                            "fn": get_avg_speed(20),
                            "label": label,
                        },
                    )
                ],
            )
        )

        map_.speedometer_id = speedometer_entity.entity_id

        # Create a countdown label
        countdown_entity = Entity()
        countdown_entity.attach(
            CountdownComponent(
                purpose="race",
                started_at=time.monotonic(),
                duration=6.0,
            )
        )
        window = get_window()
        x, y = window.window.width / 2, window.window.height
        label = pyglet.text.Label(
            "GET READY", font_size=36, x=x, y=y, anchor_x="center", anchor_y="top"
        )
        visual = Visual(kind="label", z_sort=0, value=label)
        countdown_entity.attach(
            UIVisualComponent(
                visuals=[visual],
                top=0.90,
                right=0.5,
            )
        )

        map_.race_countdown_id = countdown_entity.entity_id

        # Open the PB line file and load in the line
        try:
            with open(
                os.path.join("records", f"{map_.map_name}_pb_line.json"), "r"
            ) as f:
                map_.pb_racing_line = json.loads(f.read())
        except:
            print("no PB Line Found")
            return

        map_.pb_line_entity_id = self.create_pb_line(map_)
        map_.pb_ghost_entity_id = self.create_pb_ghost()

    def handle_race_start(self, *, map_entity_id, **kwargs):
        # Unfreeze the ship
        ship_entity = get_ship_entity()
        ship_entity["physics"].static = False

        # Set the race start time if map exists
        map_entity = Entity.find(map_entity_id)
        if not map_entity:
            return
        map_ = map_entity["map"]
        start_time = time.monotonic()
        map_.race_start_time = start_time

        # Record the first racing line point
        self.record_racing_line_point(map_, start_time)

    def handle_race_complete(self, *, map_entity_id, **kwargs):
        # Update the race completion if the map exists
        map_entity = Entity.find(map_entity_id)
        if not map_entity:
            return
        map_ = map_entity["map"]

        self.record_racing_line_point(map_, map_.race_end_time, final_point=True)

        # Calculate race duration
        new_time = map_.race_end_time - map_.race_start_time

        # Read the current records
        with open(os.path.join("records", "pb_times.json"), "r") as f:
            records = json.loads(f.read())

        # Find the record we need to check
        current_record = records.get(map_.map_name)

        # Check the record and update it if we've beaten it
        if current_record is None or new_time < current_record:
            print(f"NEW RECORD - {new_time}")
            records[map_.map_name] = new_time
            with open(os.path.join("records", "pb_times.json"), "w") as f:
                f.write(json.dumps(records, indent=2))

            # Record the final racing line point
            with open(
                os.path.join("records", f"{map_.map_name}_pb_line.json"), "w"
            ) as f:
                f.write(json.dumps(map_.racing_line))

    def update(self):
        for map_entity in Entity.with_component("map"):
            self.update_countdown(map_entity)
            map_ = map_entity["map"]
            current_time = time.monotonic()
            if len(map_.racing_line) > 0:
                self.record_racing_line_point(map_, current_time)

            if map_.pb_ghost_entity_id is not None and map_.race_start_time is not None:
                self.update_ghost(map_, current_time)
            self.update_checkpoints(map_entity)

    def update_ghost(self, map_, current_time):
        dt = current_time - map_.race_start_time
        points = enumerate(map_.pb_racing_line)
        ghost_point = list(filter((lambda x: x[1]["dt"] > dt), points))

        # Ghost already finished the race
        if len(ghost_point) == 0:
            return

        i, p = ghost_point[0]
        ghost_entity = Entity.find(map_.pb_ghost_entity_id)
        # We didn't find a ghost, nothing to update
        if ghost_entity is None:
            return

        # Update the position and rotation of the ghost via interpolation
        physics = ghost_entity["physics"]
        if i == 0:
            physics.position = V2(p["x"], p["y"])
            physics.rotation = p["r"]
        else:
            p0 = map_.pb_racing_line[i - 1]
            p1 = p
            dt_t = p1["dt"] - p0["dt"]
            dt_p = dt - p0["dt"]
            a = dt_p / dt_t
            x = p0["x"] * (1 - a) + p1["x"] * a
            y = p0["y"] * (1 - a) + p1["y"] * a
            r = p0["r"] * (1 - a) + p1["r"] * a
            physics.position = V2(x, y)
            physics.rotation = r

    def update_countdown(self, map_entity):
        for entity in Entity.with_component("countdown"):
            countdown = entity["countdown"]
            map_ = map_entity["map"]

            if entity.entity_id != map_.race_countdown_id:
                continue

            if countdown.purpose != "race":
                continue

            if not map_entity["map"].is_active:
                print("Map is not active, destroying countdown")
                entity.destroy()

            label = entity["ui visual"].visuals[0].value

            time_left = (countdown.duration + countdown.started_at) - time.monotonic()
            if time_left > 3.0:
                label.text = "Get Ready!"
            elif time_left > 2.0:
                label.text = "3"
                if countdown.last_evaluated > 3.0:
                    System.dispatch(event="PlaySound", sound="3_2_1")
            elif time_left > 1.0:
                label.text = "2"
                if countdown.last_evaluated > 2.0:
                    System.dispatch(event="PlaySound", sound="3_2_1")
            elif time_left > 0.0:
                label.text = "1"
                if countdown.last_evaluated > 1.0:
                    System.dispatch(event="PlaySound", sound="3_2_1")
            elif time_left > -1.0:
                label.text = "Go"
                if countdown.last_evaluated > 0.0:
                    System.dispatch(event="PlaySound", sound="go")
                if not countdown.completed:
                    countdown.completed = True
                    System.dispatch(
                        event="RaceStart",
                        map_name=map_entity["map"].map_name,
                        map_entity_id=map_entity.entity_id,
                    )
            else:
                entity.destroy()
            countdown.last_evaluated = time_left

    def record_racing_line_point(self, map_, at_time, final_point=False):
        entity = get_ship_entity()
        position = entity["physics"].position
        rotation = entity["physics"].rotation

        if (
            len(map_.racing_line) == 0
            or (
                V2(map_.racing_line[-1]["x"], map_.racing_line[-1]["y"]) - position
            ).length
            > 50
            or final_point
        ):
            map_.racing_line.append(
                {
                    "x": position.x,
                    "y": position.y,
                    "r": rotation,
                    "dt": at_time - map_.race_start_time,
                }
            )

    def create_pb_ghost(self):
        entity = Entity()
        entity.attach(PhysicsComponent(position=V2(0, 0), rotation=0))
        sprite = pyglet.sprite.Sprite(ASSETS[settings.selected_ship], x=0, y=0, subpixel=True)
        sprite.opacity = 127
        sprite.scale = 0.25
        game_visuals = [Visual(kind="sprite", z_sort=-10.0, value=sprite)]
        entity.attach(GameVisualComponent(visuals=game_visuals))
        return entity.entity_id

    def create_pb_line(self, map_):
        print("here")
        entity = Entity()
        points = [V2(p["x"], p["y"]) for p in map_.pb_racing_line]
        points_p = []
        for p in points:
            points_p.append(p.x)
            points_p.append(p.y)
        infinite_magenta = cycle((255, 0, 255, 50))
        fp_component = FlightPathComponent(path=points)
        fp_line_visual = Visual(
            kind="flight path",
            z_sort=-10.0,
            value=pyglet.graphics.vertex_list(
                len(points),
                ("v2f", points_p),
                (
                    "c4B",
                    list(y for x, y in zip(range(len(points) * 4), infinite_magenta)),
                ),
            ),
        )
        entity.attach(fp_component)
        entity.attach(GameVisualComponent(visuals=[fp_line_visual]))
        return entity.entity_id

    def update_checkpoints(self, map_entity):
        entities = Entity.with_component("checkpoint")
        ship_entity = get_ship_entity()
        ship_physics = ship_entity["physics"]
        next_cp = self.get_next_cp(entities)
        last_cp = self.get_last_cp(entities)

        # Check for passing through checkpoint and update checkpoints if complete
        got_checkpoint = False
        for entity in entities:
            cp = entity["checkpoint"]

            if cp.map_entity_id != map_entity.entity_id:
                continue

            if cp.cp_order != next_cp:
                continue

            physics = entity["physics"]
            if (ship_physics.position - physics.position).length < 100:
                cp.completed = True
                game_visual = entity["game visual"]
                visuals = list(sorted(game_visual.visuals, key=lambda v: v.z_sort))
                top_visual = visuals[1]
                bottom_visual = visuals[0]
                top_visual.value.image = cp.passed_image_top
                bottom_visual.value.image = cp.passed_image_bottom
                got_checkpoint = True
                System.dispatch(event="PlaySound", sound="cp_complete")
                cp.is_next = False
                if cp.cp_order == last_cp:
                    map_ = map_entity["map"]
                    map_.race_end_time = time.monotonic()
                    System.dispatch(
                        event="RaceComplete",
                        map_name=map_.map_name,
                        map_entity_id=map_entity.entity_id,
                        sound='map_win',
                    )

        if got_checkpoint:
            # If we picked up a checkpoint, we need to re-calculate what the next checkpoint is
            next_cp = self.get_next_cp(entities)

        for entity in entities:
            cp = entity["checkpoint"]
            if not cp.completed and cp.cp_order == next_cp and cp.cp_order != last_cp:
                game_visual = entity["game visual"]
                visuals = list(sorted(game_visual.visuals, key=lambda v: v.z_sort))
                top_visual = visuals[1]
                bottom_visual = visuals[0]
                top_visual.value.image = cp.next_image_top
                bottom_visual.value.image = cp.next_image_bottom
                cp.is_next = True
            if cp.cp_order == last_cp:
                game_visual = entity["game visual"]
                visuals = list(sorted(game_visual.visuals, key=lambda v: v.z_sort))
                top_visual = visuals[1]
                bottom_visual = visuals[0]
                top_visual.value.image = cp.finish_image_top
                bottom_visual.value.image = cp.finish_image_bottom

    def get_next_cp(self, entities):
        incomplete_cps = [e for e in entities if not e["checkpoint"].completed]
        if len(incomplete_cps) > 0:
            return min(e["checkpoint"].cp_order for e in incomplete_cps)
        else:
            return -1

    def get_last_cp(self, entities):
        all_checkpoints = [e for e in entities if e["checkpoint"]]
        if len(all_checkpoints) > 0:
            return max(e["checkpoint"].cp_order for e in all_checkpoints)
        else:
            return -1
