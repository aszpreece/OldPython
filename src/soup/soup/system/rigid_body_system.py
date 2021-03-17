from src.util.util import angle_between_points, get_acceleration_delta

from src.soup.engine.system import System
from src.soup.soup.components import Movement, Velocity, RigidBody


class RigidBodySystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)

    def update(self):
        rigid_bodies = set(self.ecs.filter(RigidBody.c_type_id))
        velocities = set(self.ecs.filter(Velocity.c_type_id))
        largest_rb = max(map(lambda rb: rb.get_component_by_name(
            'rigidbody').radius, rigid_bodies))

        for entity in rigid_bodies & velocities:
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
                        vel = entity.get_component_by_name('velocity')
                        vel.vel -= vec.normalize() * 0.01

    def apply(self):
        pass
