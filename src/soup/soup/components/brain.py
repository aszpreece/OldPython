import pygame as pg
from src.soup.engine.component import Component

class Brain(Component):
    
    c_type_id = 10

    def __init__(self, brain):
        self.brain = brain