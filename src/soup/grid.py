import math
import pygame as pg
from src.soup.util import clamp

class Cell:
    def __init__(self, x, y, side_len):
        self.x = x
        self.y = y

        self.entities = []


class Grid:

    def __init__(self, world_width, world_height, wu_per_cell):

        self.world_width = world_width
        self.world_height = world_height

        if (world_width <= 0 or world_height <= 0):
            raise ValueError('width and height must be greater than 0 ')

        self.wu_per_cell = wu_per_cell
        self.cells = []
        # Calculate cells in the world
        self.grid_width = math.ceil(world_width / wu_per_cell)
        self.grid_height = math.ceil(world_height / wu_per_cell)

        for x in range(self.grid_width):
            grid_list = []
            for y in range(self.grid_height):
                new_cell = Cell(x, y, wu_per_cell)
                grid_list.append(new_cell)

            self.cells.append(grid_list)

    def world_coords_to_cell_coords(self, pos):
        """Converts a word coordinate vector into a tuple containing the x and y of the cell that covers that point.
        If coordinates provided are outside range of the grid then the nearest cell will be returned.

        Args:
            pos (pygame.Vector2): The position to fetch the cell coordinates for.

        Returns:
            Tuple: x and y pair corresponding to cell coordinates.
        """
        x = math.floor(pos[0] / self.wu_per_cell)
        y = math.floor(pos[1] / self.wu_per_cell)

        clamped = self.clamp_to_cell_coords((x, y))

        return clamped

    def place_into_grid(self, entity):
        # Get the grid this entity should be in
        x, y = self.world_coords_to_cell_coords(entity._pos)

        # If the entity has just been placed in the grid it will have no _cell property.
        # If not we need to remove the entity from its old cell
        # If the entity has moved outside the bounds of the cell it should be in we need to remove it from the grid
        if entity._cell is not None and (entity._cell.x != x or entity._cell.y != y):
            self.remove_from_grid(entity)

        # Once any removing has been done set the entities cell etc
        entity._cell = self.cells[x][y]
        entity._cell.entities.append(entity)

    def remove_from_grid(self, entity):
        entity._cell.entities.remove(entity)
        entity._cell = None

    def get_nearby_entities(self, pos, range_wu):
        # Simple case, where range of check does not extend outside bounds of the cell

        sx, sy = pos
        # find top left of range to check
        tlx = sx - range_wu
        tly = sy - range_wu
        tl = self.clamp_to_world_coords((tlx, tly))

        # find bottom right of range to check
        brx = sx + range_wu
        bry = sy + range_wu
        br = self.clamp_to_world_coords((brx, bry))

        ctlx, ctly = self.world_coords_to_cell_coords(tl)
        cbrx, cbry = self.world_coords_to_cell_coords(br)

        rs = range_wu**2
        def range_filter(e):
            return (e._pos - pos).magnitude_squared() <= rs

        # Future optimization: use circle arithmetic to check if cell is in circle
        for y in range(ctly, cbry + 1):
            for x in range(ctlx, cbrx + 1):
                yield from filter(range_filter, self.cells[x][y].entities)

    def clamp_to_world_coords(self, pos):
        x = clamp(pos[0], 0, self.world_width)
        y = clamp(pos[1], 0, self.world_height)
        return x, y

    def clamp_to_cell_coords(self, pos):
        x = clamp(pos[0], 0, self.grid_width - 1)
        y = clamp(pos[1], 0, self.grid_height - 1)
        return x, y


class Entity():

    def __init__(self, grid, pos, eid):
        self.eid = eid
        self._grid = grid
        self._cell = None
        self.set_pos(pos)

    def set_pos(self, new_pos):
        self._pos = new_pos
        self._grid.place_into_grid(self)

    def __eq__(self, other):
        return self.eid == other.eid

    def get_nearby_entities(self, range_wu):
        return filter(lambda e: e.eid != self.eid, self._grid.get_nearby_entities(self._pos, range_wu))
