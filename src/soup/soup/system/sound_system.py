import math

from src.soup.engine.system import System
from src.soup.soup.components import Ear, Speaker
from src.util.util import calculate_angle_diff, angle_between_points
from random import Random


class SoundSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)
        self.rand = Random()

    def update(self):
        speaker_entities = set(self.ecs.filter(Speaker.c_type_id))
        ear_entities = set(self.ecs.filter(Ear.c_type_id))

        for ear_entity in ear_entities:
            for ear in ear_entity.get_components(Ear.c_type_id):
                ear.activation = 0

        for speaker_entity in speaker_entities:
            speakers = speaker_entity.get_components(Speaker.c_type_id)

            for speaker in speakers:
                nearby_ears = speaker_entity.get_nearby_entities(
                    speaker.max_range)
                for dist_sqr, nearby_ear in nearby_ears:
                    for ear in nearby_ear.get_components(Ear.c_type_id):
                        # make sure sound source is in ear's fov
                        ear_world_angle = (nearby_ear._rot +
                                           ear.angle) % 360

                        angle_to_entity = angle_between_points(speaker_entity._pos,
                                                               nearby_ear._pos)

                        diff_angle = calculate_angle_diff(
                            angle_to_entity, ear_world_angle)

                        if abs(diff_angle) <= ear.fov:
                            angle_multiplier = 1
                            # Inverse square law
                            # Activation is inverseley proportional to the square of the distance of the source from the ear

                            if dist_sqr > 0:
                                ear.activation += speaker.max_amplitude * \
                                    speaker.activation * angle_multiplier / dist_sqr

    def apply(self):
        pass
