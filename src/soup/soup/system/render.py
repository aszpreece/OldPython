from src.soup.soup.system.sound_system import calculate_speaker_range
from src.soup.soup.components.ear import Ear
import pygame
import pygame.gfxdraw

import math
import src.soup.engine.system
from src.soup.soup.components import Camera, Circle, Speaker
from src.soup.soup.components.eye import Eye

import math


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def draw_circle_alpha(surface, color, center, radius):
    pygame.draw.circle(surface, color, center, radius)

    return
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    surface.blit(shape_surf, target_rect)


class Render(src.soup.engine.system.System):

    parallel = False

    def __init__(self, ecs, screen):
        super().__init__(ecs)
        self.screen = screen

    def update(self):

        [camera] = self.ecs.cindex[Camera.c_type_id]
        [cm_comp] = camera.get_components(Camera.c_type_id)
        offset = camera._pos

        self.screen.fill((100, 255, 255))

        for entity in self.ecs.filter(Speaker.c_type_id):
            draw_pos = (entity._pos - offset) * cm_comp.zoom

            for speaker in entity.get_components(Speaker.c_type_id):
                speaker_range = calculate_speaker_range(
                    0.1, speaker.frequency * speaker.max_freq, speaker.amplitude * speaker.max_amplitude)
                draw_circle_alpha(self.screen, pygame.Color(
                    round(255 * speaker.frequency), 255, 0, round(100 - 100*speaker.amplitude)), draw_pos, speaker_range * cm_comp.zoom)

        # self.draw_grid(cm_comp.zoom)
        for circle in self.ecs.filter(Circle.c_type_id):

            [circle_component] = circle.get_components(Circle.c_type_id)

            draw_pos = (circle._pos - offset) * cm_comp.zoom

            pygame.draw.circle(self.screen, circle_component.colour,
                               draw_pos, circle_component.radius * cm_comp.zoom)
            if circle_component.forward_line:
                line_end = draw_pos + pygame.Vector2(math.cos(math.radians(circle._rot)), -math.sin(
                    math.radians(circle._rot))) * circle_component.radius * cm_comp.zoom
                pygame.draw.line(self.screen, 0, draw_pos, line_end)

            for eye in circle.get_components(Eye.c_type_id):

                dimensions = pygame.Vector2(
                    circle_component.radius, circle_component.radius) * circle_component.radius * cm_comp.zoom
                rect_top_left = draw_pos - dimensions
                rect = pygame.Rect(rect_top_left, dimensions * 2)
                colour = (0, (sigmoid(eye.activation)) * 100, 0)
                start_angle = eye.angle + circle._rot - eye.fov
                end_angle = eye.angle + circle._rot + eye.fov
                pygame.draw.arc(self.screen, colour, rect, math.radians(
                    start_angle), math.radians(end_angle), width=200)

            for ear in circle.get_components(Ear.c_type_id):

                dimensions = pygame.Vector2(
                    circle_component.radius * 0.5, circle_component.radius * 0.5) * circle_component.radius * cm_comp.zoom
                rect_top_left = draw_pos - dimensions
                rect = pygame.Rect(rect_top_left, dimensions * 2)

                activation = sum(ear.activations)
                if activation > 0:
                    colour = ((sigmoid(activation)) * 255, 0, 0)
                else:
                    colour = (0, 0, 0)

                start_angle = ear.angle + circle._rot - ear.fov
                end_angle = ear.angle + circle._rot + ear.fov
                pygame.draw.arc(self.screen, colour, rect, math.radians(
                    start_angle), math.radians(end_angle), width=200)

    def draw_grid(self, zoom):
        for x, ylist in enumerate(self.ecs._grid.cells):
            for y, cell in enumerate(ylist):
                multiplier = zoom * self.ecs._grid.wu_per_cell
                rx = x * multiplier
                ry = y * multiplier

                # Checkerboard pattern
                col = (0, ((x + y) % 2) * 100,
                       0) if not cell.selected else (100, 0, 0)
                cell.selected = False
                pygame.draw.rect(self.screen, col, pygame.Rect(
                    rx, ry, multiplier, multiplier))

    def apply(self):
        pass
