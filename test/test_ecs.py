import unittest
import pygame as pg
import src.soup.engine.ecs as ecs
import src.soup.engine.component as component

from src.soup.engine.builtin.velocity import Velocity
from src.soup.engine.builtin.movement import Movement


class TestECS(unittest.TestCase):
    
    def test_indexes(self):
        manager = ecs.ECS(100, 100, 10)
        v1 = Velocity(pg.Vector2(1, 2))
        e1 = manager.add_entity().attach(v1)
        e2 = manager.add_entity(pos=pg.Vector2(1,1)).attach(Velocity(pg.Vector2(0, -3)))
        self.assertDictEqual(manager.cindex, {Velocity.c_type_id: [e1, e2]})
        self.assertDictEqual(manager.eindex, {e1.eid: e1, e2.eid: e2})
        self.assertDictEqual(e1._components, {Velocity.c_type_id: [v1]})

    def test_indexes_multiple_components(self):
        class FooComponent(component.Component):
            c_type_id=3

        manager = ecs.ECS(100, 100, 10)
        e1 = manager.add_entity().attach(Velocity(pg.Vector2(1, 2))).attach(FooComponent())
        e2 = manager.add_entity(pos=pg.Vector2(1,1)).attach(Velocity(pg.Vector2(0, -3)))
        e3 = manager.add_entity(pos=pg.Vector2(1,1)).attach(FooComponent())
        self.assertDictEqual(manager.cindex, {FooComponent.c_type_id: [e1, e3], Velocity.c_type_id: [e1, e2]})
        self.assertDictEqual(manager.eindex, {e1.eid: e1, e2.eid: e2, e3.eid: e3})

    def test_movement_system(self):
        manager = ecs.ECS(100, 100, 10)
        manager.add_system(Movement(manager))
        e1 = manager.add_entity(pos=pg.Vector2(1,1)).attach(Velocity(pg.Vector2(-4, -3)))
        manager.update()
        self.assertEqual(e1._pos, pg.Vector2(-3, -2))

    