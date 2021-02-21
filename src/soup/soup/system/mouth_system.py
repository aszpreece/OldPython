import math
from src.soup.engine.system import System
from src.soup.soup.components import Mouth, Eatable
from src.soup.engine.builtin.component import Circle

class MouthSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)

    def update(self):

        mouth_entities = set(self.ecs.cindex.get(Mouth.c_type_id, []))
        self.ecs.filter(Mouth.c_type_id)
        for entity in mouth_entities:
            mouths = entity.get_components(Mouth.c_type_id)
            for mouth in mouths:
                def is_eatable(d_e_p):
                    return len(d_e_p[1].get_components(Eatable.c_type_id)) > 0
                # Find all the nearby eatables
                for distance, food in filter(is_eatable, entity.get_nearby_entities(mouth.mouth_range)):
                    # Only eat one thing per tick
                    self.ecs.remove_entity(food)
                    mouth.eaten_count += 1
                    break

    def apply(self):
        pass