import pygame as pg
from src.soup.engine.component import Component


class Ear(Component):

    c_type_id = 40

    # min frequency and max frequency and the number of equidistant buckets between that detect sound
    required_atrr = {'angle', 'fov', 'min_freq', 'max_freq', 'freq_buckets'}
    default_attr = {'activations': []}

    def __init__(self, arg_dict):
        super().__init__(arg_dict, name=None)
        # self.bucket_range = (self.min_freq - self.max_freq) / self.freq_buckets
        self.activations = [0] * self.freq_buckets
