from src.soup.soup.components.controllers.rotate_test import RotateTest
from src.soup.soup.components.controllers.cursor import Cursor
from src.soup.soup.system.eye_system import EyeSystem
from src.soup.engine.builtin.system.controller_system import ControllerSystem
import unittest
import pygame as pg
import src.soup.engine.ecs as ecs
from src.soup.soup.components.controllers.random_walk import RandomWalk
from src.soup.soup.components import Eye
from src.soup.engine.builtin.component import Camera, Circle, Friction
from src.soup.engine.builtin.system import Movement, Render, Velocity, FrictionSystem
from random import Random

if __name__ == '__main__':

    world_width = 100
    world_height = 100

    manager = ecs.ECS(world_width, world_height, 10)
    manager.add_entity(pos=pg.Vector2(0, 0)).attach(Camera(4))

    rand = Random()
    for i in range(100):
        x = rand.randrange(0, 30)
        y = rand.randrange(0, 30)
        x = 0
        y = 0
        vx = 2 * rand.random() - 1
        vy = 2 * rand.random() - 1
        vx = 0
        vy = 0
        manager.add_entity(pos=pg.Vector2(x, y)) \
            .attach(Circle(1, (100, 100, 100))) \
            .attach(Velocity(pg.Vector2(vx, vy) * 2, 1)) \
            .attach(Friction(1, 0.001)) \
            #.attach(RandomWalk())
    
    manager.add_entity(pos=pg.Vector2(50, 50), rot=180) \
        .attach(Eye(-30, 20, 30, 1, name='left')) \
        .attach(Eye(30, 20, 30, 1, name='right')) \
        .attach(Circle(2, (255, 0, 0), True)) \
        .attach(Velocity()) \
        .attach(RotateTest()) \
        .attach(Friction(1, 0.01)) \
   #     .attach(RandomWalk())


    manager.add_entity(pos=pg.Vector2(60, 60)) \
        .attach(Circle(1.5, (100, 240, 0), True)) \
    
    manager.add_entity(pos=pg.Vector2(40, 60)) \
        .attach(Circle(1.5, (100, 240, 0), True)) \
        #.attach(Cursor(manager)) \

    manager.add_entity(pos=pg.Vector2(60, 40)) \
        .attach(Circle(1.5, (100, 240, 0), True)) \

        
    manager.add_entity(pos=pg.Vector2(40, 40)) \
        .attach(Circle(1.5, (100, 240, 0), True)) \

    manager.add_system(ControllerSystem(manager))
    manager.add_system(FrictionSystem(manager))
    manager.add_system(Movement(manager))
    manager.add_system(EyeSystem(manager))

    time_delay = round(1000.0/60)
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption('Soup')
    manager.add_system(Render(manager, screen))
    while True:
        pg.init()
        screen.fill((255, 255, 255))
        pg.event.pump()
        manager.update()
        pg.display.flip()
        pg.time.delay(time_delay)  # 1 second == 1000 milliseconds
        
    pygame.display.quit()
    pygame.quit()
