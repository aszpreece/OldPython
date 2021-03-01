import pygame as pg
from src.soup.engine.component import Component


class Velocity(Component):

    c_type_id = 1
    default_attr = {
        'vel': (0.0, 0.0), 'rot_v': 0.0}

    required_attr = {

    }

    def __init__(self, arg_dict):
        super().__init__(arg_dict)
        self.vel = pg.Vector2(self.vel)
