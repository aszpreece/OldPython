import math
from src.neat.genotype import sigmoid

from src.soup.engine.system import System
from src.soup.soup.components import Ear, Speaker
from src.util.util import calculate_angle_diff, angle_between_points
from random import Random


def calculate_speaker_range(threshold, frequency, source_amp):
    return math.sqrt(source_amp / (frequency**2*threshold)) if frequency > 0 else 0


def calculate_intensity(dist_sqr, frequency, source_amp):
    # amp = 1/d^2 * 1/f^2 * source_amp
    if dist_sqr == 0:
        return source_amp
    return source_amp/(dist_sqr * frequency**2) if frequency > 0 else 0


def calculate_bucket_index(freq, ear_min, ear_max, ear_buckets):
    if freq < ear_min or freq > ear_max:
        return -1
    bucket_range = (ear_min + ear_max / ear_buckets)
    normal = freq - ear_min
    return math.floor(normal / bucket_range)


def calculate_speaker_frequency(frequency, max_freq):
    return frequency * max_freq


def calculate_energy_usage(frequency, amplitude):
    return 0 if frequency == 0 else 0.1 * 1/frequency * amplitude


class SoundSystem(System):
    parallel = False

    def __init__(self, ecs, interference_thresh=0.05):
        super().__init__(ecs)
        self.rand = Random()
        self.interference_thresh = interference_thresh

    def update(self):
        speaker_entities = set(self.ecs.filter(Speaker.c_type_id))
        ear_entities = set(self.ecs.filter(Ear.c_type_id))

        # Amplitude at any point is proportional to 1/d^2 and to 1/f^2
        # amp = 1/d^2 * 1/f^2 * source_amp
        # The max range of the wave is therefore when the amplitude of the wave reaches below some interference threshold. However this cannot reach true 0
        # thresh = 1/d^2 * 1/f^2 * source_amp
        # thresh * d^2 = 1/f^2 * source_amp
        # d^2 = (1/f^2 * source_amp) / thresh
        # Reduce divisions required
        # d^2 = 1/f^2 * source_amp * 1/thresh
        # d^2 = source_amp/(f^2*thresh)

        for ear_entity in ear_entities:
            for ear in ear_entity.get_components(Ear.c_type_id):
                for i in range(len(ear.activations)):
                    ear.activations[i] = 0

        for speaker_entity in speaker_entities:
            speakers = speaker_entity.get_components(Speaker.c_type_id)

            for speaker in speakers:
                real_freq = speaker.frequency * speaker.max_freq
                real_amp = speaker.amplitude * speaker.max_amplitude
                max_range = calculate_speaker_range(
                    self.interference_thresh, real_freq, real_amp)

                nearby_ears = speaker_entity.get_nearby_entities(max_range)

                for dist_sqr, nearby_ear in nearby_ears:
                    for ear in nearby_ear.get_components(Ear.c_type_id):
                        bucket = calculate_bucket_index(
                            real_freq, ear.min_freq, ear.max_freq, ear.freq_buckets)
                        if bucket == -1:
                            # out of hearing range
                            continue
                        # make sure sound source is in ear's fov
                        ear_world_angle = (nearby_ear._rot +
                                           ear.angle) % 360

                        angle_to_entity = angle_between_points(speaker_entity._pos,
                                                               nearby_ear._pos)

                        diff_angle = calculate_angle_diff(
                            angle_to_entity, ear_world_angle)

                        if abs(diff_angle) <= ear.fov:
                            ear.activations[bucket] += calculate_intensity(
                                dist_sqr, real_freq, real_amp)

        for ear_entity in ear_entities:
            for ear in ear_entity.get_components(Ear.c_type_id):
                for i in range(len(ear.activations)):
                    ear.activations[i] = math.tanh(ear.activations[i])

    def apply(self):
        pass
