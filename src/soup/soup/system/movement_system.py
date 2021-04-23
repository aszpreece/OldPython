from src.util.util import get_acceleration_delta

from src.soup.engine.system import System
from src.soup.soup.components import Movement, Velocity

import math


class MovementSystem(System):
    parallel = True

    def __init__(self, ecs, bounce_edges=True):
        super().__init__(ecs)
        self.bounce_edges = bounce_edges

    def get_work_data(self):
        movement = set(self.ecs.filter(Movement.c_type_id))
        velocities = set(self.ecs.filter(Velocity.c_type_id))
        return movement & velocities

    def update(self):
        def update_movement(entity):
            vel = entity.get_component_by_name('velocity')
            mov = entity.get_component_by_name('movement')
            if math.isnan(vel.vel.x) or math.isnan(vel.vel.y):
                print('foo')

            vel.vel += get_acceleration_delta(entity._rot,
                                              mov.max_a * mov.wish_acc)

            vel.rot_v += 2 * (mov.wish_rot_v_a - 0.5) * mov.max_rot_a

            if math.isnan(vel.vel.x) or math.isnan(vel.vel.y):
                print('foo')
        return update_movement

    def apply(self):
        pass
