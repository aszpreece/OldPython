from src.soup.engine.component import Component
import pygame as pg
import math
from src.soup.engine.system import System
from src.soup.soup.components import Velocity, Friction
from src.soup.soup.components.controller import Controller


class ControllerSystem(System):
    parallel = True

    def __init__(self, ecs):
        super().__init__(ecs)

    def get_work_data(self):
        controller_entities = set(
            self.ecs.cindex.get(Controller.c_type_id, []))
        return controller_entities

    def work(self):
        pass

    def work(self):
        def update_controllers(entity):
            controllers = entity.get_components(Controller.c_type_id)
            for controller in controllers:
                controller.update(entity)
        return update_controllers

    def apply(self):
        pass
