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
        pass

    def handle_fx(self, *, fx, volume=1.0, **kwargs):
        audio = Entity.with_component("audio")[0]['audio']

        player = ASSETS[fx].play()
        player.volume = volume * audio.fx_volume

