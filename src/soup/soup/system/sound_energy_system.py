from src.soup.soup.system.sound_system import calculate_energy_usage
from src.soup.soup.components.mouth import Mouth
from src.soup.soup.components.speaker import Speaker
from src.soup.soup.components import Brain
from src.soup.engine.system import System


class SoundEnergySystem(System):

    def __init__(self, ecs):
        super().__init__(ecs)

    def update(self):
        sound_entities = set(
            self.ecs.filter(Speaker.c_type_id))
        mouth_entities = set(

            self.ecs.filter(Mouth.c_type_id))
        for entity in sound_entities & mouth_entities:
            mouth = entity.get_component_by_name('mouth')
            for speaker in entity.get_components(Speaker.c_type_id):
                real_freq = speaker.frequency * speaker.max_freq
                real_amp = speaker.amplitude * speaker.max_amplitude
                energy_used = calculate_energy_usage(
                    real_freq, real_amp) * 1/60

                mouth.eaten_count -= energy_used
                mouth.eaten_count = 0 if mouth.eaten_count < 0 else mouth.eaten_count

    def apply(self):
        pass
