from src.soup.soup.components import Brain
from src.soup.engine.system import System


def update(self, entity):

    eye_left = entity.get_component_by_name('eyeL').activation
    eye_right = entity.get_component_by_name('eyeR').activation

    self.brain.set('bias', 1)
    self.brain.set('eyeL', eye_left)
    self.brain.set('eyeR', eye_right)

    self.brain.calculate()

    v = self.brain.get('v_accel')
    r = self.brain.get('r_accel')


class BrainSystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)

    def update(self):
        brain_entities = set(
            self.ecs.filter(Brain.c_type_id))
        for entity in brain_entities:
            brain = entity.get_component_by_name('brain')
            for mapping in brain.inputs:
                brain.brain.set(mapping['name'],
                                entity.get_value(mapping['from']))
            brain.brain.calculate()
            for mapping in brain.outputs:
                entity.set_value(
                    mapping['to'], brain.brain.get(mapping['name']))

    def apply(self):
        pass
