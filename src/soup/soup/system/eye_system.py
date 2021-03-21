import math
from src.neat.genotype import sigmoid

from src.soup.engine.system import System
from src.soup.soup.components import Eye
from src.soup.soup.components import Circle
from src.util.util import calculate_angle_diff, angle_between_points
from random import Random


class EyeSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)
        self.rand = Random()

    def update(self):
        eyes_entities = set(self.ecs.cindex.get(Eye.c_type_id, []))

        for entity in eyes_entities:
            eyes = entity.get_components(Eye.c_type_id)
            for eye in eyes:
                eye_world_angle = (entity._rot + eye.angle) % 360
                eye.activation = -1
                eye_range_sqrd = eye.eye_range ** 2
                for dist_squared, surrounding in filter(lambda d_e_p: d_e_p[1].has_component(Circle.c_type_id), entity.get_nearby_entities(eye.eye_range)):

                    angle_to_entity = angle_between_points(
                        surrounding._pos, entity._pos)
                    diff_angle = calculate_angle_diff(
                        angle_to_entity, eye_world_angle)

                    if abs(diff_angle) <= eye.fov:
                        # Inverse square law
                        # Activation is inverseley proportional to the square of the distance of the object from the eye
                        # In this case we take it as the normalised distance (n)
                        # n = d/r
                        # We want to calculate 1/n^2.
                        # -> n^2 = d^2/r^2
                        # -> 1/n^2 = r^2/d^2, so we don't have to do any sqrts and only one division!
                        # print(f'eye_range_sqrd: {eye_range_sqrd}')
                        # print(f'dist_squared: {dist_squared}')
                        # the max distance of

                        if dist_squared > 0:
                            eye.activation += (eye.power_multiplier *
                                               eye_range_sqrd/dist_squared)

                eye.activation = math.tanh(eye.activation)

    def apply(self):
        pass
