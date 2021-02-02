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


def normalize(val, maximum, minimum=0):
    return (val-minimum)/maximum


class CreatureBrain2D:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_movement(self) -> float:
        pass

    @abc.abstractmethod
    def get_rotation(self) -> float:
        pass

    @abc.abstractmethod
    def get_sound(self) -> float:
        pass

    @abc.abstractmethod
    def update(self, sounds, obst_in_front, x, y, obst_dist=0) -> None:
        pass


class Creature2D:

    def __init__(self, brain: CreatureBrain2D, pos: pygame.Vector2, ears, bird_id) -> None:
        self.pos = pos
        self.rotation = 0.0
        self.brain = brain
        self.alive = True
        self.speed = 0.7
        self.rotation_speed = 0.2
        self.ears = ears
        self.bird_id = bird_id

    def get_movement(self) -> float:
        return self.brain.get_movement() * self.speed

    def get_rotation(self) -> float:
        return self.brain.get_rotation() * self.rotation_speed

    def get_sound(self) -> float:
        return self.brain.get_sound()

    def update(self, sounds, in_zone, x, y, obst_dist=0) -> None:
        # Sensors per ear
        self.brain.update(sounds,
                          in_zone, x, y, obst_dist)


class Swarm2DConfig:
    def __init__(self,
                 arena_side_length=20.0,
                 zone_radius=3.0,
                 obstacle_distance: int = 30,
                 obstacle_speed=0.5,
                 moving_obstacle=False,
                 kill_on_edge=False,
                 detector_noise_std=0,
                 communication=True):

        self.arena_side_length = arena_side_length
        self.zone_radius = zone_radius
        self.obstacle_distance = obstacle_distance
        self.obstacle_speed = obstacle_speed
        self.moving_obstacle = moving_obstacle
        self.kill_on_edge = kill_on_edge
        self.detector_noise_std = detector_noise_std
        self.communication = communication


class Swarm2D:

    def __init__(self, bird_brains, config):

        self.arena_side_length = config.arena_side_length
        self.zone_radius = config.zone_radius
        self.obstacle_distance = config.obstacle_distance
        self.obstacle_speed = config.obstacle_speed
        self.moving_obstacle = config.moving_obstacle
        self.kill_on_edge = config.kill_on_edge
        self.detector_noise_std = config.detector_noise_std
        self.communication = config.communication

        self.obstacle_z = self.obstacle_distance

        self.randomize_obstacle()

        self.birds: List[Creature2D] = [Creature2D(bird_brains[i], pygame.Vector2(pos, pos), 8, i) for i, pos in enumerate(
            np.linspace(0, self.arena_side_length, len(bird_brains)))]

        self.score = 0
        self.obstacles_cleared = 0
        self.bird_edge_crashes = 0

    # Randomly select the centre of the next circle
    def randomize_obstacle(self):
        x = np.random.randint(
            self.zone_radius, self.arena_side_length-self.zone_radius)
        y = np.random.randint(
            self.zone_radius, self.arena_side_length-self.zone_radius)

        self.obstacle_centre = pygame.Vector2(x, y)
        self.obstacle_z = self.obstacle_distance

    def collision_course(self, bird):

        # Avoid normalizing vector
        if bird.pos.distance_squared_to(self.obstacle_centre) < self.zone_radius ** 2:
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

    def update(self):
        # angle of bird (cc to x axis)
        # angle between each ear
        # calculate vector of each bird to this bird

        all_bird_ear_inputs = []
        for bird in self.birds:
            increment = math.pi * 2 / bird.ears
            current_angle = bird.rotation

            to_other_birds = []
            bird_ear_inputs = []

            for other_bird in self.birds:
                if bird.bird_id == other_bird.bird_id:
                    to_other_birds.append(0)
                else:
                    diff = other_bird.pos - bird.pos
                    if diff.length_squared() > 0:
                        to_other_birds.append(
                            diff.normalize())
                    else:
                        to_other_birds.append(
                            pygame.Vector2(0, 1))

            for ear in range(bird.ears):
                x = math.cos(current_angle)
                y = math.sin(current_angle)
                ev = pygame.Vector2(x, y)
                current_angle += increment

                sound_to_ear = 0
                for i, other_bird in enumerate(self.birds):
                    if bird.bird_id == other_bird.bird_id:
                        continue
                    sound_to_ear += self.calculate_input_to_ear(
                        ev, to_other_birds[i], other_bird.get_sound())

                bird_ear_inputs.append(sound_to_ear / len(self.birds))
            all_bird_ear_inputs.append(bird_ear_inputs)

        # Update each bird
        for i, bird in enumerate(self.birds):

            delta = pygame.Vector2(bird.get_movement(), bird.get_rotation())
            bird.rotation += bird.get_rotation()
            bird.pos += pygame.Vector2(math.cos(bird.rotation),
                                       math.sin(bird.rotation)) * bird.get_movement()
            if bird.pos.x < 0:
                bird.pos.x = 0
            if bird.pos.x > self.arena_side_length:
                bird.pos.x = self.arena_side_length
            if bird.pos.y < 0:
                bird.pos.y = 0
            if bird.pos.y > self.arena_side_length:
                bird.pos.y = self.arena_side_length
            
            in_zone = self.collision_course(bird) + random.normalvariate(0, self.detector_noise_std)

            bird.update(all_bird_ear_inputs[i], in_zone, normalize(
                bird.pos.x, self.arena_side_length), normalize(
                bird.pos.y, self.arena_side_length), normalize(self.obstacle_z, self.obstacle_distance))

        self.obstacle_z -= self.obstacle_speed

        if self.obstacle_z < 0:
            # Do the collision checking
            for bird in self.birds:
                if self.collision_course(bird) != 0.5:
                    # Kill the bird
                    bird.alive = False

            # Filter out dead birds
            self.birds = list(filter(lambda bird: bird.alive, self.birds))

            # Award score based on the amount of birds
            self.score += len(self.birds)

            self.randomize_obstacle()
            self.obstacles_cleared += 1

    def all_dead(self):
        return True if len(self.birds) == 0 else False


def visualize(instance: Swarm2D, time_delay=200) -> None:
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Swarm 2D')

    scale = 20.0

    while not instance.all_dead():
        pygame.event.pump()
        screen.fill((255, 255, 255))

        pygame.draw.circle(screen, (255 * (instance.obstacle_z / instance.obstacle_distance),
                                    50, 50), instance.obstacle_centre * scale, instance.zone_radius * scale)

        for bird in instance.birds:
            pygame.draw.circle(screen, (50, math.floor(bird.get_sound() * 255), 50),
                               bird.pos * scale, 4)

        pygame.display.flip()
        pygame.time.delay(time_delay)  # 1 second == 1000 milliseconds
        instance.update()

    pygame.display.quit()
    pygame.quit()
