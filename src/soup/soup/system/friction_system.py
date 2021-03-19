from src.soup.engine.system import System
from src.soup.soup.components import Velocity, Friction
import pygame as pg
import math


class FrictionSystem(System):

    def __init__(self, ecs, gravity=9.8):
        super().__init__(ecs)
        self.gravity = gravity

    def update(self):
        # f = mu N
        vels = set(self.ecs.cindex.get(Velocity.c_type_id, []))
        friction = set(self.ecs.cindex.get(Friction.c_type_id, []))
        for es in vels & friction:
            [fric] = es.get_components(Friction.c_type_id)
            normal_force = fric.mass * self.gravity
            acceleration = fric.coef_f * normal_force
            vel = es.get_component_by_name('velocity')
            if math.isnan(vel.vel.x) or math.isnan(vel.vel.y):
                print('foo')

            delta_vel = vel.vel * acceleration
            vel.vel -= delta_vel
            if math.isnan(vel.vel.x) or math.isnan(vel.vel.y):
                print('foo')
            delta_rot_v = vel.rot_v * normal_force * fric.coef_f
            if abs(vel.rot_v) < abs(delta_rot_v):
                vel.rot_v = 0
            else:
                vel.rot_v -= delta_rot_v

    def apply(self):
        pass
    #     for vs in self.ecs.cindex.get(Velocity.c_type_id, []):
    #         old = vs._pos
    #         vel_l = vs.get_components(Velocity.c_type_id)
    #         if (len(vel_l) > 1):
    #             raise Exception('Entity cannot more than one velocity component')

    #         [vel] = vel_l
    #         vs.set_pos(vel.new)
