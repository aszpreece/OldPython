from src.soup.engine.system import System
from src.soup.soup.components.velocity import Velocity


class VelocitySystem(System):

    def __init__(self, ecs, bounce_edges=True):
        super().__init__(ecs)
        self.bounce_edges = bounce_edges

    def update(self):
        for vs in self.ecs.cindex.get(Velocity.c_type_id, []):
            old_pos = vs._pos
            old_rot = vs._rot

            vel = vs.get_component_by_name('velocity')

            vel.new_pos = old_pos + vel.vel
            vel.new_rot = old_rot + vel.rot_v

            if self.bounce_edges:
                if vel.new_pos.x < 0:
                    vel.new_pos.x = 0
                    vel.vel.x = -vel.vel.x
                if vel.new_pos.x > self.ecs.world_width:
                    vel.new_pos.x = self.ecs.world_width
                    vel.vel.x = -vel.vel.x

                if vel.new_pos.y < 0:
                    vel.new_pos.y = 0
                    vel.vel.y = -vel.vel.y
                if vel.new_pos.y > self.ecs.world_height:
                    vel.new_pos.y = self.ecs.world_height
                    vel.vel.y = -vel.vel.y

    def apply(self):
        for vs in self.ecs.cindex.get(Velocity.c_type_id, []):
            vel_l = vs.get_components(Velocity.c_type_id)
            if (len(vel_l) > 1):
                raise Exception(
                    'Entity cannot more than one velocity component')

            [vel] = vel_l
            vs.set_pos(vel.new_pos)
            vs.set_rot(vel.new_rot)
