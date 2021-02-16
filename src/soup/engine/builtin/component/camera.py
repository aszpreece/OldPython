import pygame as pg
from src.soup.engine.component import Component

class Camera(Component):
    
    c_type_id = 2

    def __init__(self, zoom):
        super().__init__('camera')
        self.zoom = zoom