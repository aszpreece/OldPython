import pygame as pg
from src.soup.engine.component import Component


class Speaker(Component):

    c_type_id = 106

    default_attr = {
        'activation': 0,
        'freq_setting': 0
    }

    required_atrr = {
        'frequency',
        'max_amplitude',
        'max_range'
        'min_freq'
        'max_freq'
    }

    def __init__(self, arg_dict):
        super().__init__(arg_dict)
