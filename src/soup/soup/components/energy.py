import pygame as pg
from src.soup.engine.component import Component

class Energy(Component):
    
    c_type_id = 12

    def __init__(self, energy):
        self.energy = energy