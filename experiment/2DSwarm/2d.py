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


class CreatureBrain:
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

    def __init__(self, brain: BirdBrain, pos: pygame.Vector2, ears, bird_id) -> None:
        self.pos = pos
        self.direction = 0
        self.brain = brain
        self.alive = True
        self.speed = 0.7
        self.ears = ears
        self.id = bird_id

    def get_wish_dir(self) -> float:
        return self.brain.get_wish_dir()

    def get_sound(self) -> float:
        return self.brain.get_sound()

    def update(self, sounds, in_zone, obst_dist=0) -> None:

        # Sensors per ear
        self.brain.update(sounds,
                          in_zone, obst_dist)


class FlappySwarmConfig:
    def __init__(self,
        arena_side_length=20.0,
        zone_radius=3.0,
        obstacle_distance: int = 30,
        obstacle_speed=0.5,
        moving_obstacle=False,
        kill_on_edge=False,
        detector_noise_std=0,
        communication=True):
        
        self.arena_side_length  = arena_side_length 
        self.zone_radius = zone_radius
        self.obstacle_distance = obstacle_distance
        self.obstacle_speed = obstacle_speed
        self.moving_obstacle = moving_obstacle
        self.kill_on_edge = kill_on_edge
        self.detector_noise_std = detector_noise_std
        self.communication = communication

class FlappySwarm:

    def __init__(self, bird_brains, config):

        self.arena_side_length=config.arena_side_length
        self.zone_radius=config.zone_radius
        self.obstacle_distance= config.obstacle_distance
        self.obstacle_speed=config.obstacle_speed
        self.moving_obstacle=config.moving_obstacle
        self.kill_on_edge=config.kill_on_edge
        self.detector_noise_std = config.detector_noise_std
        self.communication = config.communication

        self.obstacle_z=self.obstacle_distance

        self.randomize_obstacle()

        self.birds: List[Bird]=[Bird(bird_brains[i], pos) for i, pos in enumerate(
            np.linspace(0, self.arena_height, len(bird_brains)))]

        self.score=0
        self.obstacles_cleared=0

        self.bird_edge_crashes=0

    # Randomly select the centre of the next circle
    def randomize_obstacle(self):
        x = np.random.randint(self.zone_radius, self.arena_side_length-self.zone_radius)
        y = np.random.randint(self.zone_radius, self.arena_side_length-self.zone_radius)

        self.obstacle_centre = pygame.Vector2(x, y)

    def collision_course(self, bird):

        # Avoid normalizing vector
        if bird.pos.distance_squared_to(self.obstacle_centre) < self.zone_radius ** 2
            return 0.5
        else:
            return -0.5

    def calculate_input_to_ear(self, ear_vector, ear_to_source, source_noise):
        """
            ear_vector: normalized ear vector
            ear_to_source: normalized vector from ear to source of noise
            source_noise: noise being made at a point
        """
        dot = ear_vector.dot(ear_to_source)
        if dot <= 0:
            return 0
        else:
            return dot * source_noise

    def update_birds():
        # angle of bird (cc to x axis)
        # angle between each ear
        increment = math.pi * 2 / bird.ears
        current_angle = bird.direction
        # calculate vector of each bird to this bird

        all_bird_ear_inputs = []
        for bird in self.birds:
            to_other_birds = []
            bird_ear_inputs = []

            for other_bird in self.birds:
                if bird.bird_id == other_bird.bird_id:
                    continue
                to_other_birds.append((other_bird.pos - bird.pos).normalize())
            
            for ear in range(bird.ears):
                x = math.cos(current_angle)
                y = math.sin(current_angle)
                ev = pygame.Vector2(x, y)
                current_angle += increment

                sound_to_ear = 0
                for i, other_bird in enumerate(self.birds):
                    if bird.bird_id == other_bird.bird_id:
                        continue
                    sound_to_ear += self.calculate_input_to_ear(ev, to_other_birds[i], other_bird.get_sound())
                
                bird_ear_inputs.append(sound_to_ear / len(self.birds))
            all_bird_ear_inputs.append(bird_ear_inputs)

        # Update each bird
        for i, bird in enumerate(self.birds):
            in_zone = self.collision_course(bird)
            bird.update(all_bird_ear_inputs[i], in_zone, )

    def update(self):
        self.update_birds()


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
