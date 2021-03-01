import pygame as pg
from src.soup.engine.component import Component


class Movement(Component):

    c_type_id = 1

    default_attr = {
        'vel_a': 0.005, 'rot_v_a': 0.1}

    required_attr = {

    }

    def __init__(self, arg_dict):
        super().__init__(arg_dict, name='velocity')
        self.vel = pg.Vector2(self.vel)
        self.wish_acc = 0
        self.wish_rot_v_a = 0
