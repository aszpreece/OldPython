from random import Random
import pygame as pg

from src.soup.engine.system import System
from src.soup.soup.components import Mouth, Eatable
from src.soup.soup.components import Circle


class FoodSystem(System):
    parallel = False

    def __init__(self, ecs, target_food, empty_range_to_spawn):
        super().__init__(ecs)
        self.target_food = target_food
        self.empty_range_to_spawn = empty_range_to_spawn
        self.rand = Random()
        for food in range(self.target_food):
            x = self.rand.randrange(0, self.ecs.world_width)
            y = self.rand.randrange(0, self.ecs.world_height)
            self.ecs.add_entity(pos=pg.Vector2(x, y)) \
                .attach(Circle(
                    {'radius': 0.5, 'forward_line': False,
                        'colour':  (100, 240, 0)}))\
                .attach(Eatable({}))

    def update(self):

        food_on_map = len(list(self.ecs.filter(Eatable.c_type_id)))

        if food_on_map < self.target_food:
            food_to_spawn = self.target_food - food_on_map
            for i in range(food_to_spawn):
                x = self.rand.randrange(0, self.ecs.world_width)
                y = self.rand.randrange(0, self.ecs.world_height)
                in_range = self.ecs._grid.get_nearby_entities(
                    pg.Vector2(x, y), self.empty_range_to_spawn)

                if not any(filter(lambda d_e_p: d_e_p[1].has_component(Mouth.c_type_id), in_range)):
                    self.ecs.add_entity(pos=pg.Vector2(x, y)) \
                        .attach(Circle({'radius': 0.5, 'colour': (100, 100, 240), 'forward_line': True})) \
                        .attach(Eatable({}))

    def apply(self):
        pass
