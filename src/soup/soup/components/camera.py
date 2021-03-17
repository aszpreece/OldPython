import pygame as pg
from src.soup.engine.component import Component


class Camera(Component):

    c_type_id = 2
    default_attr = {'zoom': 4}
    required_atrr = {}

    def __init__(self, arg_dict):
        super().__init__(arg_dict, name='camera')
