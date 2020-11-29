# Version 1:
# Birds told distance to next obstacle

# Version 2:
# Birds not told distance to next obstacle. requiring memory

from src.neat.neat import NEAT
from experiment.run_experiment import train_neat
import random
import abc
import math
from src.neat.node_type import NodeType
from src.neat.phenotype import Phenotype
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, mod_sigmoid, relu, sigmoid
from src.neat.mutate import DefaultMutationManager
from src.neat.reproduction import DefaultReproductionManager
from src.neat.neat_config import NeatConfig
import numpy as np
from typing import List, Tuple
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
        self.speed = 1

    def get_movement(self) -> float:
        return self.brain.get_movement() * self.speed

    def get_sound(self) -> float:
        return self.brain.get_sound()

    def update(self, above_sound, below_sound, obst_in_front, dist_below, dist_above, obst_dist=0) -> None:
        self.brain.update(above_sound, below_sound,
                          obst_in_front, dist_below, dist_above, obst_dist)


class FlappySwarm:

    def __init__(self, bird_brains):

        self.arena_height = 20.0
        self.opening_size = 4.0
        self.obstacle_distance: int = 30

        self.obstacle_x = self.obstacle_distance
        # Y pos of the top of the opening
        self.obstacle_opening_y = 0
        self.randomize_obstacle()

        self.birds: List[Bird] = [Bird(bird_brains[i], pos) for i, pos in enumerate(
            np.linspace(0, self.arena_height, len(bird_brains)))]

        self.score = 0
        self.obstacles_cleared = 0

    def randomize_obstacle(self):
        self.obstacle_x = self.obstacle_distance
        self.obstacle_opening_y = random.uniform(
            0, self.arena_height - self.opening_size)

    def collision_course(self, bird):
        if bird.y < self.obstacle_opening_y or bird.y > self.obstacle_opening_y + self.opening_size:
            return True
        else:
            return False

    def update(self):

        list.sort(self.birds, key=lambda bird: bird.y)

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

            bird.update(sound_above / len(self.birds), sound_below /
                        len(self.birds), self.collision_course(bird), dist_below, dist_above, self.obstacle_x / self.obstacle_distance)

            sound_above += my_sound

        # Get the movement for the bird
        for bird in self.birds:
            new_pos = bird.y + bird.get_movement()

            if new_pos < 0 or new_pos > self.arena_height:
                bird.alive = False
            # new_pos = max(0, min(new_pos, self.arena_height))
            bird.y = new_pos

        # Filter out dead birds
        self.birds = list(filter(lambda bird: bird.alive, self.birds))

        if self.obstacle_x == 0:
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
            self.obstacle_x -= 1

    def all_dead(self):
        return True if len(self.birds) == 0 else False


def visualize(instance: FlappySwarm) -> None:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Flappy Swarm')

    scale = 20.0  # 600 / instance.arena_height

    while not instance.all_dead():
        screen.fill((255, 255, 255))

        top_rect = (instance.obstacle_x * scale, 0, 2,
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
        pygame.time.delay(300)  # 1 second == 1000 milliseconds

        instance.update()


bird_base = Genotype()

bird_base.node_genes = [
    NodeGene(0, NodeType.BIAS),  # Bias node
    NodeGene(1, NodeType.INPUT),  # Obstacle in front (1 if true 0 else)
    # Sound above (normalized for amount of birds)
    NodeGene(2, NodeType.INPUT),

    NodeGene(3, NodeType.INPUT),  # Sound below
    NodeGene(4, NodeType.INPUT),  # Distance to next obstacle
    # Movement of bird
    NodeGene(5, NodeType.OUTPUT, activation_func=mod_sigmoid),
    # Sound from bird
    NodeGene(6, NodeType.OUTPUT, activation_func=sigmoid),
    NodeGene(7, NodeType.INPUT),  # Dist below
    NodeGene(8, NodeType.INPUT),  # Dist above
]

# Set up perceptron
bird_base.connection_genes = [
    ConnectionGene(0, 1, 5, 0),
    ConnectionGene(1, 2, 5, 0),
    ConnectionGene(2, 3, 5, 0),
    ConnectionGene(3, 4, 5, 0),
    ConnectionGene(4, 5, 5, 0),

    ConnectionGene(5, 1, 6, 0),
    ConnectionGene(6, 2, 6, 0),
    ConnectionGene(7, 3, 6, 0),
    ConnectionGene(8, 4, 6, 0),
    ConnectionGene(9, 5, 6, 0),

    ConnectionGene(10, 7, 5, 0),
    ConnectionGene(11, 8, 6, 0),
]

bird_base.conn_innov_start = 11
bird_base.node_innov_start = 8


class NeatBirdBrain(BirdBrain):

    def __init__(self, genotype: Genotype) -> None:
        self.phenotype = Phenotype(genotype)

    def get_movement(self) -> float:
        return self.phenotype.node_activations.get(5, 0)

    def get_sound(self) -> float:
        return self.phenotype.node_activations.get(6, 0)

    def update(self, above_sound, below_sound, obst_in_front, dist_below, dist_above, obst_dist=0) -> None:
        self.phenotype.calculate({
            0: 1,
            1: obst_in_front,
            2: above_sound,
            3: below_sound,
            4: obst_dist,
            7: dist_below,
            8: dist_above
        })


def bird_fitness(genotype: Genotype):
    # Create a bunch of bird brains and put them in a simulation
    brains = [NeatBirdBrain(genotype) for i in range(6)]
    simulation = FlappySwarm(brains)

    while len(simulation.birds) > 2 and simulation.obstacles_cleared < 30:
        simulation.update()

    return simulation.score


def result_func(neat: NEAT):
    if neat.population.best_individual is not None and neat.generation_num % 20 == 0:
        brains = [NeatBirdBrain(neat.population.best_individual)
                  for i in range(6)]
        simulation = FlappySwarm(brains)
        visualize(simulation)


config = NeatConfig(
    activation_func=sigmoid,
    fitness_function=bird_fitness,
    base_genotype=bird_base,
    reproduction=DefaultReproductionManager(),
    generation_size=150,
    mutation_manager=DefaultMutationManager(3, 3),
    species_target=10,
    species_mod=0.1,
    prob_crossover=0.8,
    weight_perturb_scale=1,
    new_weight_power=0.8
)

train_neat(bird_fitness, config, 1320, result_func=result_func)
