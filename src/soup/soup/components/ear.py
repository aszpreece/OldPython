import pygame as pg
from src.soup.engine.component import Component


class Ear(Component):

    c_type_id = 11

    def __init__(self, arg_dict):
        super().__init__(arg_dict, required_atrr={'angle'}, name=None)
