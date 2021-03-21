from src.soup.soup.components import Brain
from src.soup.engine.system import System
import math


class AverageDensitySystem(System):

    def __init__(self, ecs, check_distance):
        super().__init__(ecs)
        self.check_distance = check_distance
        self.average_density_per_update = []

    def update(self):
        brain_entities = set(
            self.ecs.filter(Brain.c_type_id))

        average_dist_list = []
        for entity in brain_entities:
            total = 0
            count = 0
            for dist_sqr, neighbour in entity.get_nearby_entities(self.check_distance):
                dist = math.sqrt(dist_sqr)
                total += dist
                count += 1

            average = total / count if count > 0 else 0
            average_dist_list.append(average)

        total_average = sum(average_dist_list) / len(average_dist_list)
        self.average_density_per_update.append(total_average)

    def apply(self):
        pass
