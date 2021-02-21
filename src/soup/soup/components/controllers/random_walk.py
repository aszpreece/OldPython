import math
import pygame as pg
from random import Random

from src.soup.soup.components.controller import Controller


class RandomWalk(Controller):
    def __init__(self):
        super().__init__()
        self.rand = Random()

    def update(self, entity):
        vel = entity.get_component_by_name('velocity')
        vel.vel += pg.Vector2(math.cos(math.radians(entity._rot)), math.sin(math.radians(entity._rot))) * self.v_acceleration * 0.005
        vel.rot_v += (self.rand.random() -0.5) * 0.01
