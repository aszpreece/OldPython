import pygame as pg
from src.soup.engine.component import Component


class Eatable(Component):

    c_type_id = 14

    def __init__(self, arg_dict):
        super().__init__(arg_dict)
        pass
