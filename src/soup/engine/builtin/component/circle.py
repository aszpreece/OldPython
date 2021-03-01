import pygame as pg
from src.soup.engine.component import Component


class Circle(Component):

    c_type_id = 3

    def __init__(self, arg_dict):
        super().__init__(arg_dict, default_attr={'forward_line': True}, required_atrr={
            'radius', 'colour', 'forward_line'}, name='circle')
