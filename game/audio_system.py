# Music: https://www.chosic.com/free-music/all/
# background_audio = pyglet.media.load(os.path.join('assets', 'background_music_test.mp3'))

# player = pyglet.media.Player()
# player.loop = True
# player.queue(background_audio)
# player.play()

from .ecs import *
from .assets import ASSETS
from .settings import settings

class AudioSystem(System):
    def setup(self):
        self.subscribe("PlaySound", self.handle_sound)
        self.subscribe("RaceComplete", self.handle_sound)

    def handle_sound(self, *, sound, **kwargs):
        # if sound not playing play, else nothing
        if settings.audio:
            try:
                print('sound')
                ASSETS[sound].play()
            # Not the best way to handle this probably but it is working
            except:
                pass
# System.dispatch(event="PlaySound", sound="map_win")
