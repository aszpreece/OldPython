import pygame as pg
from src.soup.engine.component import Component


class RigidBody(Component):

    c_type_id = 102

    default_attr = {}

    required_atrr = {
        'radius'
    }

    def __init__(self, arg_dict):
        super().__init__(arg_dict, name='rigidbody')
