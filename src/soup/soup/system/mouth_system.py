import math
from src.soup.engine.system import System
from src.soup.soup.components import Mouth, Eatable
from src.soup.soup.components import Circle


class MouthSystem(System):
    parallel = True

    def __init__(self, ecs):
        super().__init__(ecs)

    def get_work_data(self):
        return self.ecs.filter(Mouth.c_type_id)

    def update(self):

        def update_mouths(entity):
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

        return update_mouths

    def apply(self):
        pass
