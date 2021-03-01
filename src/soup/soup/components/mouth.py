
from src.soup.engine.component import Component


class Mouth(Component):

    c_type_id = 15

    def __init__(self, arg_dict):
        super().__init__(arg_dict, default_attr={
            'eaten_count': 0, 'mouth_range': 1}, required_atrr={})
