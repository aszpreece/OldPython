from src.soup.engine.system import System
from src.soup.soup.components import Velocity, Friction
import pygame as pg
import math


class FrictionSystem(System):
    parallel = True

    def __init__(self, ecs, gravity=9.8):
        super().__init__(ecs)
        self.gravity = gravity

    def get_work_data(self):
        vels = set(self.ecs.filter(Velocity.c_type_id))
        friction = set(self.ecs.filter(Friction.c_type_id))
        return vels & friction

    def work(self):
        # f = mu N

        def update_friction(es):
            [fric] = es.get_components(Friction.c_type_id)
            normal_force = fric.mass * self.gravity
            acceleration = fric.coef_f * normal_force
            vel = es.get_component_by_name('velocity')

            delta_vel = vel.vel * acceleration
            vel.vel -= delta_vel

            delta_rot_v = vel.rot_v * normal_force * fric.coef_f
            if abs(vel.rot_v) < abs(delta_rot_v):
                vel.rot_v = 0
            else:
                vel.rot_v -= delta_rot_v
        return update_friction

    def apply(self):
        pass
