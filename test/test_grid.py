import unittest
from src.soup.grid import Grid, Entity
import pygame as pg


def order_entities(e):
    return e.eid


class GridTest(unittest.TestCase):

    def test_shape(self):
        # Test grid that is 100 word units squared
        # Each cell should therefore be 10*10. There should be 110 cells
        # And the width and height of the cell array should be 11, 10
        grid = Grid(110, 100, 10)
        self.assertEqual(grid.grid_width, 11)
        self.assertEqual(grid.grid_height, 10)

    def test_add_entity(self):
        grid = Grid(110, 100, 10)
        entity = Entity(grid, pg.Vector2(2, 2), 1)
        self.assertEqual(entity._cell.x, 0)
        self.assertEqual(entity._cell.y, 0)
        entities = grid.cells[0][0].entities
        self.assertEqual(len(entities), 1)

    def test_move_entity(self):
        grid = Grid(110, 100, 10)
        entity = Entity(grid, pg.Vector2(0, 1), 1)
        # New position is in next cell across horizontally...
        entity.set_pos(pg.Vector2(11, 5))

        self.assertEqual(entity._cell.x, 1)
        self.assertEqual(entity._cell.y, 0)

        old_cell = grid.cells[0][0].entities
        self.assertEqual(len(old_cell), 0)

        new_cell = grid.cells[1][0].entities
        self.assertEqual(len(new_cell), 1)

        # New position is vertically below

        entity.set_pos(pg.Vector2(13, 10.1))

        self.assertEqual(entity._cell.x, 1)
        self.assertEqual(entity._cell.y, 1)

        old_cell = grid.cells[1][0].entities
        self.assertEqual(len(old_cell), 0)

        new_cell = grid.cells[1][1].entities
        self.assertEqual(len(new_cell), 1)

    def test_cell_edges(self):

        grid = Grid(10, 2, 1)
        entity = Entity(grid, pg.Vector2(0.999, 0.999), 1)

        self.assertEqual(entity._cell.x, 0)
        self.assertEqual(entity._cell.y, 0)

        grid = Grid(10, 2, 1)
        entity = Entity(grid, pg.Vector2(0, 0), 1)

        self.assertEqual(entity._cell.x, 0)
        self.assertEqual(entity._cell.y, 0)

        grid = Grid(10, 2, 1)
        entity = Entity(grid, pg.Vector2(1, 1), 1)

        self.assertEqual(entity._cell.x, 1)
        self.assertEqual(entity._cell.y, 1)

    def test_cell_edges(self):

        grid = Grid(10, 2, 1)
        entity = Entity(grid, pg.Vector2(0.999, 0.999), 1)

        self.assertEqual(entity._cell.x, 0)
        self.assertEqual(entity._cell.y, 0)

        grid = Grid(10, 2, 1)
        entity = Entity(grid, pg.Vector2(0, 0), 1)

        self.assertEqual(entity._cell.x, 0)
        self.assertEqual(entity._cell.y, 0)

        grid = Grid(10, 2, 1)
        entity = Entity(grid, pg.Vector2(1, 1), 1)

        self.assertEqual(entity._cell.x, 1)
        self.assertEqual(entity._cell.y, 1)

    def test_distance(self):
        grid = Grid(10, 10, 1)
        e0 = Entity(grid, pg.Vector2(4.5, 4.5), 1)
        e1 = Entity(grid, pg.Vector2(4.6, 4.6), 2)
        e2 = Entity(grid, pg.Vector2(5.1, 4.5), 3)
        e3 = Entity(grid, pg.Vector2(10, 0.2), 4)

        # Happy path, in range of 1
        nearby = list(e1.get_nearby_entities(1))
        nearby.sort(key=order_entities)
        self.assertListEqual(nearby, [e0, e2])

        # Not in range of anything
        # Also on the edge of the grid!
        nearby = list(e3.get_nearby_entities(1))
        nearby.sort(key=order_entities)
        self.assertListEqual(nearby, [])

    def test_distance_on_edge(self):
        # Entities clustered around top left
        grid = Grid(10, 10, 1)
        e0 = Entity(grid, pg.Vector2(0.5, 0.5), 1)
        e1 = Entity(grid, pg.Vector2(1.5, 1.5), 2)
        e2 = Entity(grid, pg.Vector2(1.5, 0.5), 3)
        e3 = Entity(grid, pg.Vector2(0.5, 1.5), 4)

        nearby = list(e0.get_nearby_entities(1))
        nearby.sort(key=order_entities)
        self.assertListEqual(nearby, [e2, e3])

        # Entities clustered around bottom right
        grid = Grid(10, 10, 1)
        e0 = Entity(grid, pg.Vector2(10, 10), 1)
        e1 = Entity(grid, pg.Vector2(9, 9), 2)
        e2 = Entity(grid, pg.Vector2(9, 10), 3)
        e3 = Entity(grid, pg.Vector2(10, 9), 4)

        nearby = list(e0.get_nearby_entities(1))
        nearby.sort(key=order_entities)
        self.assertListEqual(nearby, [e2, e3])

    def test_cross_cell_search(self):
        grid = Grid(10, 10, 1)
        e0 = Entity(grid, pg.Vector2(5.1, 5.1), 1)
        e1 = Entity(grid, pg.Vector2(4, 5.1), 2)
        e2 = Entity(grid, pg.Vector2(3.9, 5.1), 3)
        # Verified 6.2 does not work because of floating point innaccuracies
        e3 = Entity(grid, pg.Vector2(6.19999, 5.1), 4)
        e4 = Entity(grid, pg.Vector2(6.3, 5.1), 5)

        nearby = list(e0.get_nearby_entities(1.1))
        nearby.sort(key=order_entities)
        self.assertListEqual(nearby, [e1, e3])

    def test_cross_grid_search(self):
        grid = Grid(10, 10, 1)
        e0 = Entity(grid, pg.Vector2(10, 10), 1)
        e1 = Entity(grid, pg.Vector2(9, 9), 2)
        e2 = Entity(grid, pg.Vector2(9, 10), 3)
        e3 = Entity(grid, pg.Vector2(10, 9), 4)
        e4 = Entity(grid, pg.Vector2(5, 2), 5)
        e5 = Entity(grid, pg.Vector2(2, 4), 6)
        e6 = Entity(grid, pg.Vector2(1, 10), 7)
        e7 = Entity(grid, pg.Vector2(2.2, 4.4), 8)

        nearby = list(grid.get_nearby_entities(pg.Vector2(5, 4.9), 100))
        nearby.sort(key=order_entities)

        self.assertListEqual(nearby, [e0, e1, e2, e3, e4, e5, e6, e7])
