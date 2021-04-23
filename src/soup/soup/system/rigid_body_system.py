from src.util.util import angle_between_points, get_acceleration_delta

from src.soup.engine.system import System
from src.soup.soup.components import Movement, Velocity, RigidBody
import math


class RigidBodySystem(System):
    parallel = True

    def __init__(self, ecs):
        super().__init__(ecs)

    def get_work_data(self):
        rigid_bodies = set(self.ecs.filter(RigidBody.c_type_id))
        velocities = set(self.ecs.filter(Velocity.c_type_id))
        return rigid_bodies & velocities

    def update(self):
        # TODO get this back in
        # largest_rb = max(map(lambda rb: rb.get_component_by_name(
        #     'rigidbody').radius, rigid_bodies))
        largest_rb = 0

        def update_rigid_bodies(entity):
            # vel = entity.get_component_by_name('velocity')
            rb = entity.get_component_by_name('rigidbody')
            potential_interset = entity.get_nearby_entities(
                rb.radius + largest_rb)
            for dist, interset_entity in potential_interset:
                rb2 = interset_entity.get_component_by_name('rigidbody')
                if rb2 is None:
                    continue
                if dist < (rb.radius + rb2.radius) ** 2:
                    # find collision normal
                    vec = (interset_entity._pos - entity._pos)
                    if vec.length_squared() > 0:
                        if math.isnan(vel.vel.x) or math.isnan(vel.vel.y):
                            print('foo')

                        vel = entity.get_component_by_name('velocity')
                        vel.vel -= vec.normalize() * 0.01
                        if math.isnan(vel.vel.x) or math.isnan(vel.vel.y):
                            print('foo')
        return update_rigid_bodies

    def apply(self):
        pass
