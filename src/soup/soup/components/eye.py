from src.soup.engine.component import Component


class Eye(Component):

    c_type_id = 12
    default_attr = {'activation': -1}
    required_atrr = {
        'angle', 'eye_range', 'fov', 'power_multiplier'}

    def __init__(self, arg_dict):
        super().__init__(arg_dict)
