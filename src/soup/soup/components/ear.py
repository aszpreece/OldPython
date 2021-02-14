import pygame as pg
from src.soup.engine.component import Component

class Ear(Component):
    
    c_type_id = 11

    def __init__(self, angle):
        self.angle = angle