import unittest
import pygame as pg
import src.soup.engine.ecs as ecs
import src.soup.engine.component as component

from src.soup.soup.components import Velocity
from src.soup.engine.builtin.system import Movement


def strip_tuple(d_e_p):
    return d_e_p[1]


class TestECS(unittest.TestCase):

    def test_indexes(self):
        manager = ecs.ECS(100, 100, 10)
        v1 = Velocity(pg.Vector2(1, 2))
        e1 = manager.add_entity().attach(v1)
        e2 = manager.add_entity(pos=pg.Vector2(1, 1)).attach(
            Velocity(pg.Vector2(0, -3)))
        self.assertDictEqual(manager.cindex, {Velocity.c_type_id: {e1, e2}})
        self.assertDictEqual(manager.eindex, {e1.eid: e1, e2.eid: e2})
        self.assertDictEqual(e1._components, {Velocity.c_type_id: [v1]})

    def test_indexes_multiple_components(self):
        class FooComponent(component.Component):
            c_type_id = 3

        manager = ecs.ECS(100, 100, 10)
        e1 = manager.add_entity().attach(Velocity(pg.Vector2(1, 2))).attach(FooComponent())
        e2 = manager.add_entity(pos=pg.Vector2(1, 1)).attach(
            Velocity(pg.Vector2(0, -3)))
        e3 = manager.add_entity(pos=pg.Vector2(1, 1)).attach(FooComponent())
        self.assertDictEqual(manager.cindex, {FooComponent.c_type_id: {
                             e1, e3}, Velocity.c_type_id: {e1, e2}})
        self.assertDictEqual(
            manager.eindex, {e1.eid: e1, e2.eid: e2, e3.eid: e3})

    def test_movement_system(self):
        manager = ecs.ECS(100, 100, 10)
        manager.add_system(Movement(manager, bounce_edges=False))
        e1 = manager.add_entity(pos=pg.Vector2(1, 1)).attach(
            Velocity(pg.Vector2(-4, -3)))
        manager.update()
        self.assertEqual(e1._pos, pg.Vector2(-3, -2))

    def test_movement_system_bounce(self):
        manager = ecs.ECS(100, 100, 10)
        manager.add_system(Movement(manager, bounce_edges=True))
        e1 = manager.add_entity(pos=pg.Vector2(1, 1)).attach(
            Velocity(pg.Vector2(-4, -3)))
        manager.update()
        self.assertEqual(e1._pos, pg.Vector2(0, 0))

    def test_remove_entity(self):
        manager = ecs.ECS(100, 100, 10)
        e1 = manager.add_entity(pos=pg.Vector2(1, 1)).attach(
            Velocity(pg.Vector2(-4, -3)))
        e2 = manager.add_entity(pos=pg.Vector2(2, 2)).attach(
            Velocity(pg.Vector2(-4, -3)))
        e3 = manager.add_entity(pos=pg.Vector2(3, 3)).attach(
            Velocity(pg.Vector2(-4, -3)))
        e4 = manager.add_entity(pos=pg.Vector2(4, 4)).attach(
            Velocity(pg.Vector2(-4, -3)))

        self.assertTrue(e1.eid in manager.eindex)
        self.assertTrue(e1 in manager.cindex[Velocity.c_type_id])
        self.assertTrue(e1 in list(
            map(strip_tuple, e2.get_nearby_entities(10))))
        manager.remove_entity(e1)
        self.assertFalse(e1 in manager.cindex[Velocity.c_type_id])
        self.assertFalse(e1.eid in manager.eindex)
        self.assertFalse(e1 in list(
            map(strip_tuple, e2.get_nearby_entities(10))))
