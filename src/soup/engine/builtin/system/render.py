import pygame
import pygame.gfxdraw

import math
import src.soup.engine.system
from src.soup.engine.builtin.component import Camera, Circle

class Render(src.soup.engine.system.System):


    def __init__(self, ecs, screen):
        super().__init__(ecs)
        self.screen = screen
    
    def update(self):

        [camera] = self.ecs.cindex[Camera.c_type_id]
        [cm_comp] = camera.get_components(Camera.c_type_id)
        offset = camera._pos


        self.screen.fill((100, 255, 255))
        self.draw_grid(cm_comp.zoom)
        for circle in self.ecs.cindex.get(Circle.c_type_id, []):
            [circle_component] = circle.get_components(Circle.c_type_id)

            draw_pos = (circle._pos - offset) * cm_comp.zoom
            pygame.draw.circle(self.screen, circle_component.colour, draw_pos, circle_component.radius * cm_comp.zoom)
            if circle_component.forward_line:
                line_end = draw_pos + pygame.Vector2(math.cos(circle._rot), math.sin(circle._rot)) * circle_component.radius * cm_comp.zoom
                pygame.draw.line(self.screen, 0, draw_pos, line_end)

    # Draw the grid for debugging purposes
    def draw_grid(self, zoom):
        for x, ylist in enumerate(self.ecs._grid.cells):
            for y, cell in enumerate(ylist):
                multiplier = zoom * self.ecs._grid.wu_per_cell
                rx = x * multiplier
                ry = y * multiplier
                
                # Checkerboard pattern
                col = (0, ((x + y) % 2) * 100 ,0) if not cell.selected else (100,0,0)
                cell.selected = False
                pygame.draw.rect(self.screen, col, pygame.Rect(rx, ry, multiplier, multiplier))
            
    def apply(self):
        pass
