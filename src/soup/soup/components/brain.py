import math
from src.soup.engine.component import Component


class Brain(Component):
    c_type_id = 24
    default_attr = {'brain': None, 'outputs': [], 'inputs': []}
    required_atrr = set()

    def __init__(self, arg_dict):
        super().__init__(arg_dict)
