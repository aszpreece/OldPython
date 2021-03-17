import math
from src.util.util import get_acceleration_delta
import pygame as pg
from random import Random

from src.soup.soup.components.controller import Controller


class RotateTest(Controller):

    default_attr = {}
    required_atrr = set()

    def __init__(self, arg_dict):
        super().__init__(arg_dict)

    def update(self, entity):
        vel = entity.get_component_by_name('velocity')
        pressed = pg.key.get_pressed()
        if pressed[pg.K_LEFT]:
            vel.rot_v += 1
        elif pressed[pg.K_RIGHT]:
            vel.rot_v -= 1
        if pressed[pg.K_UP]:
            vel.vel += get_acceleration_delta(entity._rot, 0.1)
        elif pressed[pg.K_DOWN]:
            vel.vel -= get_acceleration_delta(entity._rot, 0.1)
