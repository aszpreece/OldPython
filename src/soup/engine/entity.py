class Entity():

    def __init__(self, grid, pos, eid, ecs):
        self.eid = eid
        self._grid = grid
        self._cell = None
        self.set_pos(pos)
        self.ecs = ecs
        self._components = {}

    def set_pos(self, new_pos):
        self._pos = new_pos
        self._grid.place_into_grid(self)

    def __eq__(self, other):
        return self.eid == other.eid

    def get_nearby_entities(self, range_wu):
        return filter(lambda e: e.eid != self.eid, self._grid.get_nearby_entities(self._pos, range_wu))

    def attach(self, component):
        self.ecs.attach(self.eid, component)
        return self

    def get_component(self, c_type_id):
        return self._components.get(c_type_id, [])