from . import ecs


class RenderSystem(ecs.System):

    def update(self):
        window_entity = list(ecs.Entity.with_component("window"))[0]
        window = window_entity['window']
        camera = window.camera_position
        viewport = window.viewport_size
        width, height = window.window.width, window.window.height

        layer_paralax = [10, 8, 2]
        for paralax, sprite in zip(layer_paralax, window.background_layers):

            sl = int(camera.x // paralax)
            sr = int(camera.x // paralax + width)
            st = int(camera.y // paralax + height)
            sb = int(camera.y // paralax)

            ixl = int(sl // sprite.width)
            ixr = int(sr // sprite.width)
            ixt = int(st // sprite.height)
            ixb = int(sb // sprite.height)

            for ox in range(ixl, ixr + 1):
                for oy in range(ixb, ixt + 1):
                    sprite.x = -camera.x // paralax + ox * sprite.width
                    sprite.y = -camera.y // paralax + oy * sprite.height
                    sprite.draw()

        entities = ecs.Entity.with_component("sprite")
        for entity in entities:
            physics = entity['physics']
            if physics is None:
                continue
            sprite = entity['sprite']
            sprite.x = physics.position.x - camera.x + width // 2
            sprite.y = physics.position.y - camera.y + height // 2
            sprite.rotation = float(-physics.rotation)
            sprite.draw()

