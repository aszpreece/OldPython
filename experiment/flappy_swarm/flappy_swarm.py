# Version 1:
# Birds told distance to next obstacle

# Version 2:
# Birds not told distance to next obstacle. requiring memory

import random
import abc
import math

import numpy as np
from typing import List
import pygame


class BirdBrain:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_movement(self) -> float:
        pass

    @abc.abstractmethod
    def get_sound(self) -> float:
        pass

    @abc.abstractmethod
    def update(self, above_sound, below_sound, obst_in_front, dist_below, dist_above, obst_dist=0) -> None:
        pass


class Bird:

    def __init__(self, brain: BirdBrain, y: float) -> None:
        self.y = y
        self.brain = brain
        self.alive = True
        self.speed = 0.7

    def get_movement(self) -> float:
        return self.brain.get_movement() * self.speed

    def get_sound(self) -> float:
        return self.brain.get_sound()

    def update(self, above_sound, below_sound, obst_in_front, dist_below, dist_above, obst_dist=0) -> None:
        self.brain.update(above_sound, below_sound,
                          obst_in_front, dist_below, dist_above, obst_dist)


class FlappySwarmConfig:
    def __init__(self,
        arena_height=20.0,
        opening_size=3.0,
        obstacle_distance: int = 30,
        obstacle_speed=0.5,
        moving_obstacle=False,
        kill_on_edge=False,
        detector_noise_std=0):
        
        self.arena_height  = arena_height 
        self.opening_size = opening_size
        self.obstacle_distance = obstacle_distance
        self.obstacle_speed = obstacle_speed
        self.moving_obstacle = moving_obstacle
        self.kill_on_edge = kill_on_edge
        self.detector_noise_std = detector_noise_std

class FlappySwarm:

    def __init__(self, bird_brains, config):

        self.arena_height=config.arena_height
        self.opening_size=config.opening_size
        self.obstacle_distance= config.obstacle_distance
        self.obstacle_speed=config.obstacle_speed
        self.moving_obstacle=config.moving_obstacle
        self.kill_on_edge=config.kill_on_edge
        self.detector_noise_std = config.detector_noise_std

        self.obstacle_x=self.obstacle_distance
        # Y pos of the top of the opening
        self.obstacle_opening_y=0
        self.original_opening_y=0

        self.randomize_obstacle()

        self.birds: List[Bird]=[Bird(bird_brains[i], pos) for i, pos in enumerate(
            np.linspace(0, self.arena_height, len(bird_brains)))]

        self.score=0
        self.obstacles_cleared=0

        self.bird_edge_crashes=0

    def randomize_obstacle(self):
        self.obstacle_x=self.obstacle_distance
        self.original_opening_y=random.uniform(
            0, self.arena_height - self.opening_size)
        self.obstacle_opening_y=self.original_opening_y

    def shift_obstacle(self):
        self.obstacle_opening_y=self.original_opening_y + math.sin((self.obstacle_x /
                                                                      self.obstacle_distance) * math.pi * 2) * self.opening_size
        self.obstacle_opening_y=max(
            0, min(self.obstacle_opening_y, self.arena_height - self.opening_size))

    def collision_course(self, bird):
        if bird.y < self.obstacle_opening_y or bird.y > self.obstacle_opening_y + self.opening_size:
            return 1
        else:
            return 0

    def update(self):

        list.sort(self.birds, key = lambda bird: bird.y)

        # Gather the inputs to the birds and update them
        total_sound = 0
        for bird in self.birds:
            total_sound += bird.get_sound()

        sound_above = 0
        prev_y = 0
        for index, bird in enumerate(self.birds):

            my_sound = bird.get_sound()

            sound_below = total_sound - sound_above - my_sound

            dist_above = (bird.y - prev_y) / self.arena_height

            next_y = self.arena_height
            if index + 1 < len(self.birds):
                next_y = self.birds[index + 1].y

            dist_below = (next_y - bird.y) / self.arena_height

            # bird.update(above_sound, below_sound, int(self.collision_course(
            #     bird)) - 0.5, dist_below, dist_above, self.obstacle_x / self.obstacle_distance)

            bird.update(sound_above / len(self.birds), sound_below /
                        len(self.birds), self.collision_course(bird) +  random.normalvariate(0, self.detector_noise_std), dist_below, dist_above, self.obstacle_x / self.obstacle_distance)

            prev_y=bird.y
            sound_above += my_sound

        # Get the movement for the bird
        for bird in self.birds:
            new_pos=bird.y + bird.get_movement()

            if self.kill_on_edge and (new_pos < 0 or new_pos > self.arena_height):
                bird.alive=False
                self.bird_edge_crashes += 1
            else:
                new_pos=max(0, min(new_pos, self.arena_height))

            bird.y=new_pos

        # Filter out dead birds
        self.birds=list(filter(lambda bird: bird.alive, self.birds))

        if self.obstacle_x < 0:
            # Do the collision checking
            for bird in self.birds:
                if self.collision_course(bird):
                    # Kill the bird
                    bird.alive = False

            # Filter out dead birds
            self.birds = list(filter(lambda bird: bird.alive, self.birds))

            # Award score based on the amount of birds
            self.score += len(self.birds)

            self.randomize_obstacle()
            self.obstacles_cleared += 1
        else:
            self.obstacle_x -= self.obstacle_speed
            if self.moving_obstacle:
                self.shift_obstacle()

    def all_dead(self):
        return True if len(self.birds) == 0 else False


def visualize(instance: FlappySwarm, time_delay=200) -> None:
    pygame.init()

    screen=pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Flappy Swarm')

    scale=20.0  # 600 / instance.arena_height

    while not instance.all_dead():
        pygame.event.pump()
        screen.fill((255, 255, 255))

        top_rect=(instance.obstacle_x * scale, 0, 2,
                    instance.obstacle_opening_y * scale)
        # Draw top of obstacle
        pygame.draw.rect(screen, (200, 100, 100), top_rect)

        top_of_bottom = (instance.obstacle_opening_y +
                         instance.opening_size) * scale
        bottom_height = instance.arena_height * scale - top_of_bottom
        bottom_rect = (instance.obstacle_x * scale,
                       top_of_bottom, 2, bottom_height)
        # Draw bottom of obstacle
        pygame.draw.rect(screen, (200, 100, 100),
                         bottom_rect)

        for bird in instance.birds:
            pygame.draw.circle(screen, (100, math.floor(bird.get_sound() * 255), 100),
                               (1, bird.y * scale), 4)

        pygame.display.flip()
        pygame.time.delay(time_delay)  # 1 second == 1000 milliseconds
        instance.update()

    pygame.display.quit()
    pygame.quit()
