from src.soup.engine.component import Component


class Eye(Component):

    c_type_id = 12

    def __init__(self, arg_dict):
        super().__init__(arg_dict, default_attr={}, required_atrr={
            'angle', 'eye_range', 'fov', 'power_multiplier'})
