    
from src.soup.engine.component import Component

class Mouth(Component):
    
    c_type_id = 15

    def __init__(self, mouth_range = 1, name=None):
        super().__init__(name)
        self.mouth_range = mouth_range
        self.eaten_count = 0