from src.soup.engine.entity import Entity
from src.soup.engine.grid import Grid
import pygame as pg
from pathos.pools import ProcessPool


class ECS:
    def __init__(self, world_width, world_height, wu_per_cell, cores_to_use):
        self.next_entity_id = 0
        self.eindex = {}
        self.cindex = {}
        self.systems = []
        self._grid = Grid(world_width, world_height, wu_per_cell)
        self.world_width = world_width
        self.world_height = world_height
        self.wu_per_cell = wu_per_cell
        self.current_tick = 0
        self.pool = ProcessPool(nodes=cores_to_use)

    def add_entity(self, pos=pg.Vector2(0, 0), rot=0):
        nid = self.next_entity_id
        e = Entity(self._grid, pos, nid, self, rot)
        self.next_entity_id += 1
        self.eindex[nid] = e
        return e

    def attach(self, eid, component):
        self.eindex[eid]._components.setdefault(
            component.c_type_id, []).append(component)
        self.cindex.setdefault(component.c_type_id, set()
                               ).add(self.eindex[eid])

    def add_system(self, system, ticks_between_runs=0):
        self.systems.append(system)
        system.ticks_between_runs = ticks_between_runs
        system.tick_counter = 0

    def filter(self, c_type_id):
        yield from self.cindex.get(c_type_id, set())

    def update(self):

        # Parallelize these loops
        self.current_tick += 1
        for system in self.systems:
            system.tick_counter += 1
            if system.ticks_between_runs == system.tick_counter:
                system.tick_counter = 0
                if system.parallel == True:
                    work_data = system.get_work_data()
                    self.pool.map(system.work, work_data)
                else:
                    system.update()
                system.apply()

    def remove_entity(self, entity):
        self._grid.remove_from_grid(entity)
        for key, component_list in entity._components.items():
            # This should probably be changed so it stores a set instead to avoid O(n) removal

            for component in component_list:
                self.cindex[component.c_type_id].remove(entity)

        del self.eindex[entity.eid]
