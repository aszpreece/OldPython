import pygame as pg
from src.soup.engine.component import Component

class Friction(Component):
    
    c_type_id = 4

    def __init__(self, mass, coef_f):
        super().__init__('friction')
        self.mass = mass
        self.coef_f = coef_f 
