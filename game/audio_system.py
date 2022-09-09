# Music: https://www.chosic.com/free-music/all/
# background_audio = pyglet.media.load(os.path.join('assets', 'background_music_test.mp3'))

# player = pyglet.media.Player()
# player.loop = True
# player.queue(background_audio)
# player.play()

from .ecs import *
from .assets import ASSETS


class AudioSystem(System):
    def setup(self):
        self.subscribe("PlaySound", self.handle_sound)

    def handle_sound(self, *, sound, **kwargs):
        ASSETS[sound].play()
