import unittest
import pygame as pg
import src.soup.engine.ecs as ecs
from src.soup.engine.builtin.component import Camera, Circle
from src.soup.engine.builtin.system import Movement, Render
from random import Random

if __name__ == '__main__':

    world_width = 100
    world_height = 100

    manager = ecs.ECS(world_width, world_height, 10)
    manager.add_entity(pos=pg.Vector2(0, 0)).attach(Camera())

    rand = Random()
    for i in range(100):
        x = rand.randrange(0, world_width)
        y = rand.randrange(0, world_height)

        manager.add_entity(pos=pg.Vector2(x, y)).attach(Circle(2, (100, 100, 100)))
    
    manager.add_system(Movement(manager))

    time_delay = 100
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
