import math
import pygame as pg
from random import Random
from src.soup.soup.components import Camera

from src.soup.soup.components.controller import Controller


class Cursor(Controller):
    def __init__(self, ecs):
        super().__init__()
        self.rand = Random()
        self.ecs = ecs

    def update(self, entity):
        pos = pg.Vector2(pg.mouse.get_pos())
        camera = self.ecs.cindex.get(Camera.c_type_id, None)
        if camera is not None:
            [cam] = camera
            cam_component = cam.get_component_by_name('camera')
            entity.set_pos(pos / cam_component.zoom)
