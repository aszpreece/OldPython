from src.soup.engine.component import Component

class Eye(Component):
    
    c_type_id = 12

    def __init__(self, angle, eye_range, fov, power_multiplier,name=None):
        super().__init__(name)
        self.angle = angle % 360
        self.eye_range = eye_range
        self.activation = 0
        self.fov = fov
        self.power_multiplier = power_multiplier