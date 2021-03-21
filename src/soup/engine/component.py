def load_component(dict):
    class_name = dict['class']
    module_name = 'src.soup.soup.components'
    data = dict['data']

    module = __import__(module_name,  fromlist=[class_name])
    class_ = getattr(module, class_name)
    instance = class_(data)
    return instance


class Component:
    c_type_id = -1

    def __init__(self, arg_dict, name=None) -> None:
        self.name = name

        required_set = set(self.required_atrr)
        allowed_set = set(self.default_attr.keys()).union({'name'})
        # set(allowed_attr)

        if not required_set.issubset(arg_dict.keys()):
            missing_keys = required_set - arg_dict.keys()
            raise ValueError(
                f'Component dictionary definition for {self.__class__} is missing the following required keys: {missing_keys}')
        arg_dict_keys = set(arg_dict.keys())
        if not arg_dict_keys.issubset(required_set.union(allowed_set)):
            extra_keys = arg_dict_keys - (required_set.union(allowed_set))
            raise ValueError(
                f'Component dictionary definition for {self.__class__} contains extra keys that are not defined in the defaults or required attributes: {extra_keys}')
        self.__dict__.update(self.default_attr)
        self.__dict__.update(arg_dict)

    def __eq__(self, other):
        return self.c_type_id == other.c_type_id
