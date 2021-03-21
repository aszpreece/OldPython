import pygame as pg
from src.soup.engine.component import Component


class Speaker(Component):

    c_type_id = 106

    # Travel distance of a wave in the simulation is as such:
    # 1/f * a
    # max distance

    default_attr = {
        'amplitude': 0,  # Controls the amplitude of the outputted wave. Should be 0 to 1
        'frequency': 0  # Controls the frequency of the outputted wave. Should be 0 to 1
    }

    required_atrr = {
        'max_amplitude',  # max amplitude of wave produced.
        'max_freq'
    }

    def __init__(self, arg_dict):
        super().__init__(arg_dict)
