from src.soup.engine.entity import Entity
from src.soup.engine.grid import Grid
import pygame as pg

class ECS:
    def __init__(self, world_width, world_height, wu_per_cell):
        self.next_entity_id = 0
        self.eindex = {}
        self.cindex = {}
        self.systems = []
        self._grid = Grid(world_width, world_height, wu_per_cell)
        self.world_width = world_width
        self.world_height = world_height
        self.wu_per_cell = wu_per_cell

    def add_entity(self, pos=pg.Vector2(0, 0)):
        nid = self.next_entity_id
        e = Entity(self._grid, pos, nid, self)
        self.next_entity_id += 1
        self.eindex[nid] = e
        return e
    
    def attach(self, eid, component):
        self.eindex[eid]._components.setdefault(component.c_type_id, []).append(component)
        self.cindex.setdefault(component.c_type_id, []).append(self.eindex[eid])
    
    def add_system(self, system):
        self.systems.append(system)

    def filter(self, c_type_id):
        yield from self.cindex.get(c_type_id, [])

    def update(self):
        # Parallelize these loops
        for system in self.systems:
            system.update()
        for system in self.systems:
            system.apply()
