import pygame as pg
from src.soup.engine.component import Component

class Eatable(Component):
    
    c_type_id = 14

    def __init__(self, name=None):
        super().__init__(name)
        pass