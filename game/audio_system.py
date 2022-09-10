# Music: https://www.chosic.com/free-music/all/
# background_audio = pyglet.media.load(os.path.join('assets', 'background_music_test.mp3'))

# player = pyglet.media.Player()
# player.loop = True
# player.queue(background_audio)
# player.play()

from .ecs import *
from .assets import ASSETS
from .settings import settings
from .components import AudioComponent
from .common import *

class AudioSystem(System):
    def setup(self):
        self.subscribe("PlaySound", self.handle_sound)
        self.subscribe("RaceComplete", self.handle_sound)

    def update(self):
        inputs = get_inputs()
        if inputs.w and not inputs.boost:
            self.handle_sound(sound="regular_thrust", loop=True)
            # self.handle_sound(sound="rocket_booster", off=True)
        # see if we have any boost
        elif inputs.boost:
            # self.handle_sound(sound="rocket_booster", loop=True)
            self.handle_sound(sound="regular_thrust", off=True)
        else:
            self.handle_sound(sound="regular_thrust", off=True)
            # self.handle_sound(sound="rocket_booster", off=True)

    def handle_sound(self, *, sound, loop=False, off=False, **kwargs):
        # if sound not playing play, else nothing
        entities = Entity.with_component("audio")
        player = None
        for entity in entities:
            audio = entity['audio']
            if audio.audio == sound:
                player = audio.player
                player_entity = entity
        if player:
            if player.playing:
                if off:
                    player.pause()
                    # player.seek(0)
                return
            elif loop and not off:
                player.play()
            elif not off:
                player_entity['audio'].player = ASSETS[sound].play()
        elif not off:
            entity = Entity()
            player = ASSETS[sound].play()
            if loop:
                player.loop = True
            entity.attach(AudioComponent(audio=sound,loop=loop, player=player))

