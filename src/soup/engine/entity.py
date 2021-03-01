import json
from src.soup.engine.component import load_component


class Entity():

    def __init__(self, grid, pos, eid, ecs, rot=0):
        self.eid = eid
        self._grid = grid
        self._cell = None
        self.set_pos(pos)
        self.ecs = ecs
        self._components = {}
        self._rot = rot
        self._components_by_name = {}

    def set_pos(self, new_pos):
        self._pos = new_pos
        self._grid.place_into_grid(self)

    def set_rot(self, new_rot):
        self._rot = new_rot % 360

    def get_nearby_entities(self, range_wu):
        return filter(lambda d_e_p: d_e_p[1].eid != self.eid, self._grid.get_nearby_entities(self._pos, range_wu))

    def attach(self, component):
        if component.name:
            if component.name in self._components_by_name:
                raise Exception(
                    'Cannot attach two components with the same name.')
            self._components_by_name[component.name] = component
        self.ecs.attach(self.eid, component)
        return self

    def get_components(self, c_type_id):
        return self._components.get(c_type_id, [])

    def has_component(self, c_type_id):
        return c_type_id in self._components

    def get_component_by_name(self, name):
        return self._components_by_name.get(name, None)

    def __eq__(self, other):
        return self.eid == other.eid

    def __hash__(self):
        return hash(self.eid)

    def from_json(self, entity_json):
        data = json.loads(entity_json)
        for component in data['components']:
            self.attach(load_component(component))

    def set_value(self, name, value):
        [component, property] = name.split('.')
        if hasattr(self.get_component_by_name(component), property):
            setattr(component, property, value)
        else:
            raise ValueError('Given value does not exist.')

    def get_value(self, name):
        [component, property] = name.split('.')
        if hasattr(self.get_component_by_name(component), property):
            return getattr(component, property)
        else:
            raise ValueError('Given value does not exist.')
