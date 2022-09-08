from . import ecs
import time

class CheckpointSystem(ecs.System):

    def get_next_cp(self, entities):
        incomplete_cps = [e for e in entities if not e['checkpoint'].completed]
        if len(incomplete_cps) > 0:
            return min(e['checkpoint'].cp_order for e in incomplete_cps)
        else:
            return -1

    def get_last_cp(self, entities):
        all_checkpoints = [e for e in entities if e['checkpoint']]
        if len(all_checkpoints) > 0:
            return max(e['checkpoint'].cp_order for e in all_checkpoints)
        else:
            return -1

    # def get_last_cp(self, entities):
    def update(self):
        ship_entity = ecs.Entity.with_component("input")[0]
        ship_physics = ship_entity['physics']
        entities = ecs.Entity.with_component("checkpoint")
        next_cp = self.get_next_cp(entities)
        last_cp = self.get_last_cp(entities)
        got_checkpoint = False

        # Check for passing through checkpoint and update checkpoints if complete
        for entity in entities:
            cp = entity['checkpoint']
            if cp.cp_order != next_cp:
                continue

            physics = entity['physics']
            if (ship_physics.position - physics.position).length < 100:
                cp.completed = True
                game_visual = entity['game visual']
                visuals = list(sorted(game_visual.visuals, key=lambda v: v.z_sort))
                top_visual = visuals[1]
                bottom_visual = visuals[0]
                top_visual.value.image = cp.passed_image_top
                bottom_visual.value.image = cp.passed_image_bottom
                got_checkpoint = True
                cp.is_next = False
                if cp.cp_order == last_cp:
                    ecs.System.inject(ecs.Event(kind='MapComplete'))

        if got_checkpoint:
            # If we picked up a checkpoint, we need to re-calculate what the next checkpoint is
            next_cp = self.get_next_cp(entities)

        for entity in entities:
            cp = entity['checkpoint']
            if not cp.completed and cp.cp_order == next_cp and cp.cp_order != last_cp:
                game_visual = entity['game visual']
                visuals = list(sorted(game_visual.visuals, key=lambda v: v.z_sort))
                top_visual = visuals[1]
                bottom_visual = visuals[0]
                top_visual.value.image = cp.next_image_top
                bottom_visual.value.image = cp.next_image_bottom
                cp.is_next = True
            if cp.cp_order == last_cp:
                game_visual = entity['game visual']
                visuals = list(sorted(game_visual.visuals, key=lambda v: v.z_sort))
                top_visual = visuals[1]
                bottom_visual = visuals[0]
                top_visual.value.image = cp.finish_image_top
                bottom_visual.value.image = cp.finish_image_bottom
                end_time = time.monotonic()
            

