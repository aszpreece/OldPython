from src.util.util import get_acceleration_delta

from src.soup.engine.system import System
from src.soup.soup.components import Movement, Velocity


class MovementSystem(System):

    def __init__(self, ecs, bounce_edges=True):
        super().__init__(ecs)
        self.bounce_edges = bounce_edges

    def update(self):
        movement = set(self.ecs.filter(Movement.c_type_id))
        velocities = set(self.ecs.filter(Velocity.c_type_id))
        for entity in movement & velocities:
            vel = entity.get_component_by_name('velocity')
            mov = entity.get_component_by_name('movement')

            vel.vel += get_acceleration_delta(entity._rot,
                                              mov.max_a * mov.wish_acc)

            vel.rot_v += 2 * (mov.wish_rot_v_a - 0.5) * mov.max_rot_a

    def apply(self):
        pass
