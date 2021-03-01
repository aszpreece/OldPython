
import unittest
from src.soup.engine.component import Component


class Required(Component):

    c_type_id = 12

    def __init__(self, arg_dict, name=None):
        super().__init__(arg_dict, default_attr={}, required_atrr={
            'angle', 'eye_range', 'fov', 'power_multiplier'}, name=name)


class Default(Component):

    c_type_id = 15

    def __init__(self, arg_dict, name=None):
        super().__init__(arg_dict, default_attr={
            'eaten_count': 0, 'mouth_range': 1}, required_atrr={}, name=name)


class RequiredAndDefault(Component):

    c_type_id = 15

    def __init__(self, arg_dict, name=None):
        super().__init__(arg_dict, default_attr={
            'eaten_count': 0, 'mouth_range': 1}, required_atrr={'bobs'}, name=name)


class TestComponentDictInit(unittest.TestCase):

    def test_only_required(self):
        arg_dict = {
            'angle': 100, 'eye_range': 101, 'fov': 102, 'power_multiplier': 103
        }
        component = Required(arg_dict=arg_dict)

        self.assertDictContainsSubset(arg_dict, component.__dict__)

        for key, item in arg_dict.items():
            self.assertEqual(item, component.__dict__[key])

    def test_only_defaults(self):
        arg_dict = {}
        component = Default(arg_dict=arg_dict)

        self.assertDictContainsSubset(arg_dict, component.__dict__)

        for key, item in {'eaten_count': 0, 'mouth_range': 1}.items():
            self.assertEqual(item, component.__dict__[key])

    def test_defaults_and_required(self):
        arg_dict = {'bobs': 100}
        component = RequiredAndDefault(arg_dict=arg_dict)

        self.assertDictContainsSubset(arg_dict, component.__dict__)

        for key, item in {'eaten_count': 0, 'mouth_range': 1, 'bobs': 100}.items():
            self.assertEqual(item, component.__dict__[key])

    def test_rejects_extra_both_required_and_default(self):
        arg_dict = {'bobs': 100, 'IAMEXTRA': 1010101}

        error = False
        try:
            component = RequiredAndDefault(arg_dict=arg_dict)
        except ValueError:
            error = True

        self.assertEqual(error, True)

    def test_rejects_extra_required(self):
        arg_dict = {'bobs': 100, 'IAMEXTRA': 1010101}

        error = False
        try:
            component = Required(arg_dict=arg_dict)
        except ValueError:
            error = True

        self.assertEqual(error, True)

    def test_rejects_extra_default(self):
        arg_dict = {'IAMEXTRA': 1010101}

        error = False
        try:
            component = Default(arg_dict=arg_dict)
        except ValueError:
            error = True

        self.assertEqual(error, True)

    def test_rejects_missing_required(self):
        arg_dict = {
            'angle': 100, 'eye_range': 101, 'fov': 102
        }

        error = False
        try:
            component = Required(arg_dict=arg_dict)
        except ValueError:
            error = True

        self.assertEqual(error, True)

    def test_rejects_missing_required_and_default(self):
        arg_dict = {
            'eaten_count': 1
        }

        error = False
        try:
            component = Required(arg_dict=arg_dict)
        except ValueError:
            error = True

        self.assertEqual(error, True)
