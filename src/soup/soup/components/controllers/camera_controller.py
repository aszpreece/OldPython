import pygame as pg

from src.soup.soup.components.controller import Controller


class CameraController(Controller):
    def __init__(self, camera_acceleration=0.01):
        super().__init__()
        self.camera_acceleration = camera_acceleration

    def update(self, entity):
        vel = entity.get_component_by_name('velocity')
        cam = entity.get_component_by_name('camera')
        if vel is None:
            return

        pressed = pg.key.get_pressed()
        if pressed[pg.K_LEFT]:
            vel.vel.x -= 1 * self.camera_acceleration
        elif pressed[pg.K_RIGHT]:
            vel.vel.x += 1 * self.camera_acceleration
        if pressed[pg.K_UP]:
            vel.vel.y -= 1 * self.camera_acceleration
        elif pressed[pg.K_DOWN]:
            vel.vel.y += 1 * self.camera_acceleration

        if pressed[pg.K_z]:
            cam.zoom += 1
        elif pressed[pg.K_x]:
            cam.zoom -= 1
