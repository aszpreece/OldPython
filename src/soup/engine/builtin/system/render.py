import pygame
import src.soup.engine.system
from src.soup.engine.builtin.component import Camera, Circle

class Render(src.soup.engine.system.System):


    def __init__(self, ecs, screen):
        super().__init__(ecs)
        self.screen = screen
    
    def update(self):

        [camera] = self.ecs.cindex[Camera.c_type_id]
        [cm_comp] = camera.get
        offset = camera._pos
        zoom = camera

        self.screen.fill((100, 255, 255))
        for circle in self.ecs.cindex.get(Circle.c_type_id, []):
            [circle_component] = circle.get_component(Circle.c_type_id)
            pygame.draw.circle(self.screen, circle_component.colour, (circle._pos - offset) * , circle_component.radius)



    def apply(self):
        pass
