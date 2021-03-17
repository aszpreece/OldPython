import pygame as pg
from src.soup.engine.component import Component


class Ear(Component):

    c_type_id = 40

    required_atrr = {'angle', 'fov'}
    default_attr = {'activation': 0}

    def __init__(self, arg_dict):
        super().__init__(arg_dict, name=None)
