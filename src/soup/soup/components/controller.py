import pygame as pg
from src.soup.engine.component import Component


class Controller(Component):
    """Abstract component that is intended to execute scripts
    """
    c_type_id = 10
    default_attr = {}
    required_atrr = set()

    def __init__(self, arg_dict, name=None):
        super().__init__(arg_dict, name)

    def update(self):
        pass
