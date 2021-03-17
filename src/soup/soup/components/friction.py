import pygame as pg
from src.soup.engine.component import Component


class Friction(Component):

    c_type_id = 4
    default_attr = {}
    required_atrr = {'mass', 'coef_f'}

    def __init__(self, arg_dict):
        super().__init__(arg_dict, name='friction')
