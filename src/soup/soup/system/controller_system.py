from src.soup.engine.component import Component
import pygame as pg
import math
from src.soup.engine.system import System
from src.soup.soup.components import Velocity, Friction
from src.soup.soup.components.controller import Controller


class ControllerSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)

    def update(self):
        controller_entities = set(
            self.ecs.cindex.get(Controller.c_type_id, []))
        for entity in controller_entities:
            controllers = entity.get_components(Controller.c_type_id)
            for controller in controllers:
                controller.update(entity)

    def apply(self):
        pass
