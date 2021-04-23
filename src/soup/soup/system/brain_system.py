from os import cpu_count
from src.soup.soup.components import Brain
from src.soup.engine.system import System
import multiprocessing as mp


class BrainSystem(System):
    parallel = True

    def __init__(self, ecs):
        super().__init__(ecs)

    def get_work_data(self):
        return set(
            self.ecs.filter(Brain.c_type_id))

    def work(self):
        def update_brain(entity):
            brain = entity.get_component_by_name('brain')
            for mapping in brain.inputs:
                if mapping.get('type', None) == 'array':
                    arr = entity.get_value(mapping['from'])
                    for i in range(mapping.get('size', 0)):
                        brain.brain.set(mapping['name'] + f'__{i}', arr[i])
                else:
                    brain.brain.set(mapping['name'],
                                    entity.get_value(mapping['from']))

            brain.brain.calculate()
            for mapping in brain.outputs:
                entity.set_value(
                    mapping['to'], brain.brain.get(mapping['name']))

        return update_brain

    def apply(self):
        return None
