
from src.soup.engine.component import Component
from src.soup.soup.components.velocity import Velocity
import src.soup.engine.ecs as ecs
import json
import pygame as pg

import unittest


class TestComponent1(Component):

    c_type_id = 1

    def __init__(self, arg_dict, name=None):
        super().__init__(arg_dict, default_attr={}, required_atrr={
            'testy1'}, name=name)


class TestComponent2(Component):

    c_type_id = 2

    def __init__(self, arg_dict, name=None):
        super().__init__(arg_dict, default_attr={
            'testy2': 0, 'testy3': 1}, required_atrr={}, name=name)


class TestComponentDictInit(unittest.TestCase):

    def test_loads_json(self):
        entity_data = {
            'components': [
                {
                    'class': 'TestComponent1',
                    'module': 'test_load_component_json',
                    'data': {
                        'testy1': 1010
                    }
                },
                {
                    'class': 'TestComponent2',
                    'module': 'test_load_component_json',
                    'data': {
                        'testy2': 40404
                    }
                }

            ]
        }

        entity_json = json.dumps(entity_data)
        manager = ecs.ECS(100, 100, 10)
        e1 = manager.add_entity().from_json(entity_json)
        component_ones = list(manager.filter(TestComponent1.c_type_id))
        component_twos = list(manager.filter(TestComponent2.c_type_id))

        self.assertEqual(len(component_ones), 1)
        self.assertEqual(len(component_twos), 1)

        for entity in component_ones:
            component1list = entity.get_components(TestComponent1.c_type_id)
            self.assertEqual(len(component1list), 1)
            for comp1 in component1list:
                self.assertEqual(comp1.testy1, 1010)

        for entity in component_twos:
            component2list = entity.get_components(TestComponent2.c_type_id)
            self.assertEqual(len(component2list), 1)
            for comp2 in component2list:
                self.assertEqual(comp2.testy2, 40404)

    def test_loads_name(self):
        entity_data = {
            'components': [
                {
                    'class': 'TestComponent1',
                    'module': 'test_load_component_json',
                    'data': {
                        'name': 'FOOBAR',
                        'testy1': 1010
                    }
                },
                {
                    'class': 'TestComponent2',
                    'module': 'test_load_component_json',
                    'data': {
                        'name': 'BARFOO',
                        'testy2': 40404,
                        'testy3': 'I am a test'
                    }
                }

            ]
        }

        entity_json = json.dumps(entity_data)
        manager = ecs.ECS(100, 100, 10)
        e1 = manager.add_entity().from_json(entity_json)
        component_ones = list(manager.filter(TestComponent1.c_type_id))

        for entity in component_ones:
            component1 = entity.get_component_by_name('FOOBAR')
            component2 = entity.get_component_by_name('BARFOO')
            self.assertIsNotNone(component1)
            self.assertIsNotNone(component2)

    def test_external_load(self):
        entity_data = {
            'components': [
                {
                    'class': 'Velocity',
                    'module': 'src.soup.soup.components.velocity',
                    'data': {
                        'name': 'velocity',
                        'vel': (0, 0),
                        'rot_v': -1
                    }
                },
                {
                    'class': 'TestComponent2',
                    'module': 'test_load_component_json',
                    'data': {
                        'name': 'BARFOO',
                        'testy2': 40404,
                        'testy3': 'I am a test'
                    }
                }
            ]
        }

        entity_json = json.dumps(entity_data)
        manager = ecs.ECS(100, 100, 10)
        e1 = manager.add_entity().from_json(entity_json)
        component_ones = list(manager.filter(TestComponent1.c_type_id))

        for entity in component_ones:
            component1 = entity.get_component_by_name('velocity')
            component2 = entity.get_component_by_name('BARFOO')
            self.assertIsNotNone(component1)
            self.assertIsNotNone(component2)

            self.assertEqual(component1.vel, pg.Vector2(0, 0))
