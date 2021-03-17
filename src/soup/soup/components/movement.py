import pygame as pg
from src.soup.engine.component import Component


class Movement(Component):

    c_type_id = 102

    default_attr = {
        'max_a': 0.005, 'max_rot_a': 0.1, 'wish_acc': 0, 'wish_rot_v_a': 0
    }

    required_atrr = {}

    def __init__(self, arg_dict):
        super().__init__(arg_dict, name='movement')
