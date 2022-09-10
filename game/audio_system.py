import pyglet

from .ecs import *
from .assets import ASSETS
from .settings import settings
from .components import AudioComponent
from .common import *

class AudioSystem(System):
    def setup(self):
        self.subscribe("PlayFX", self.handle_fx)
        entity = Entity()
        entity.attach(AudioComponent())

    def update(self):
        ship_entity = get_ship_entity()
        ship = ship_entity['ship']
        physics = ship_entity['physics']
        thrusting = (physics.acceleration.length > 0.0)

        if ship.boosting:
            self.start_loop('boost_sound')
        elif thrusting:
            self.start_loop('thrust_sound')
        else:
            self.stop_loop('boost_sound')
            self.stop_loop('thrust_sound')

    @property
    def audio(self):
        return Entity.with_component("audio")[0]['audio']

    def start_loop(self, fx, volume=1.0):
        audio = self.audio
        loops = [p for f, p in audio.fx_loops if f == fx]
        if len(loops) > 0:
            return
        player = ASSETS[fx].play()
        player.loop = True
        audio.fx_loops.append((fx, player))


    def stop_loop(self, fx):
        audio = self.audio
        loops = [p for f, p in audio.fx_loops if f == fx]
        if len(loops) > 0:
            player = loops[0]
            audio.fx_loops.remove((fx, player))
            player.pause()

    def handle_fx(self, *, fx, volume=1.0, **kwargs):
        audio = self.audio

        player = ASSETS[fx].play()
        player.volume = volume * audio.fx_volume

