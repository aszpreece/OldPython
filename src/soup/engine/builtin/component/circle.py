import pygame as pg
from src.soup.engine.component import Component

class Circle(Component):
    
    c_type_id = 3

    def __init__(self, radius, colour):
        super().__init__('circle')
        self.radius = radius
        self.colour = colour