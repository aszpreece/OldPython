from src.soup.engine.system import System
from src.soup.engine.builtin.component.velocity import Velocity

class Movement(System):

    def __init__(self, ecs):
        super().__init__(ecs)
    
    def update(self):
        for vs in self.ecs.cindex.get(Velocity.c_type_id, []):
            old = vs._pos
            vel_l = vs.get_component(Velocity.c_type_id)
            if (len(vel_l) > 1):
                raise Exception('Entity cannot more than one velocity components')
            [vel] = vel_l
            vel.new = old + vel.vel

    def apply(self):
        for vs in self.ecs.cindex.get(Velocity.c_type_id, []):
            old = vs._pos
            vel_l = vs.get_component(Velocity.c_type_id)
            if (len(vel_l) > 1):
                raise Exception('Entity cannot more than one velocity components')
            
            [vel] = vel_l
            vs.set_pos(vel.new)
            