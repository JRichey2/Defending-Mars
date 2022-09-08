from . import ecs
from .ecs import Event
from . import settings
from pyglet import clock
import pyglet


class TimingSystem(ecs.System):

    def initiate_gravity_acc(self):
        settings.ACCELERATION = True
        settings.GRAVITY = True
        settings.BOOST = True

    def countdown_test(self):
        print('3')

    clock.schedule_once(countdown_test,2)
    clock.schedule_once(initiate_gravity_acc,4)