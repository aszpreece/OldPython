import pygame as pg
from src.soup.engine.component import Component

class Velocity(Component):
    
    c_type_id = 1

    def __init__(self, vel= pg.Vector2(0, 0)):
        super().__init__('velocity')
        self.vel = vel