from . import ecs


class CheckpointSystem(ecs.System):

    def get_next_cp(self, entities):
        incomplete_cps = [e for e in entities if not e['checkpoint'].completed]
        if len(incomplete_cps) > 0:
            return min(e['checkpoint'].cp_order for e in incomplete_cps)
        else:
            return -1

    def update(self):
        ship_entity = ecs.Entity.with_component("input")[0]
        ship_physics = ship_entity['physics']
        entities = ecs.Entity.with_component("checkpoint")
        next_cp = self.get_next_cp(entities)
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

        if got_checkpoint:
            # If we picked up a checkpoint, we need to re-calculate what the next checkpoint is
            next_cp = self.get_next_cp(entities)

        for entity in entities:
            cp = entity['checkpoint']
            if not cp.completed and cp.cp_order == next_cp:
                game_visual = entity['game visual']
                visuals = list(sorted(game_visual.visuals, key=lambda v: v.z_sort))
                top_visual = visuals[1]
                bottom_visual = visuals[0]
                top_visual.value.image = cp.next_image_top
                bottom_visual.value.image = cp.next_image_bottom
                cp.is_next = True

