import pygame as pg
from src.soup.engine.component import Component


class Controller(Component):
    """Abstract component that is intended to execute scripts
    """    
    c_type_id = 10

    def __init__(self):
        super().__init__()

    def update(self):
        self.brain.update()