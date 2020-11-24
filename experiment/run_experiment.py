
import random
import math
from src.neat.mutate import DefaultMutationManager
from src.neat.reproduction import DefaultReproductionManager, ReproductionManager
from src.neat.neat_config import NeatConfig
from typing import List, Tuple

from matplotlib import pyplot as plt
from matplotlib.pyplot import title, xlabel, ylabel
from src.neat.neat import NEAT
from src.neat.phenotype import Phenotype
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.ui.graphnetwork import create_graph
import numpy as np

import logging
from typing import List, Tuple


def train_neat(base_genotype: Genotype, fitness_func, result_func=lambda neat: None):

    config = NeatConfig(
        fitness_func,
        base_genotype=base_genotype,
        reproduction=DefaultReproductionManager(),
        generation_size=150,
        mutation_manager=DefaultMutationManager(3, 3),
        species_target=10
    )
    neat = NEAT(config)

    plt.ion()

    fig, axarr = plt.subplots(3, figsize=(6, 8))
    plt.subplots_adjust(wspace=0.5, hspace=1)
    fig.show()

    error = []
    complexity = []
    species_count = []

    score = 0
    generation = 0
    old_score = 0
    while True:
        generation += 1
        solution = neat.run_generation()
        score = solution.fitness
        if solution != None:
            if old_score != score:
                print(f'Score for generation {generation} is {score}')

            old_score = score

            error.append(score)
            complexity.append(solution.get_complexity())

            axarr[0].clear()
            axarr[0].set(title="Fitness",
                         xlabel='Generation', ylabel='Fitness')
            axarr[0].plot(error)

            axarr[1].clear()
            axarr[1].set(title="Complexity",
                         xlabel='Generation', ylabel='Count')
            axarr[1].plot(complexity)
            axarr[1].legend(["Nodes", "Connections", "Enabled Connections"])

            species_count.append(len(neat.species))

            axarr[2].clear()
            axarr[2].set(title="Species",
                         xlabel='Generation', ylabel='Count')
            axarr[2].plot(species_count)
            axarr[2].legend(["Species"])

            result_func(neat)

            fig.canvas.draw()
            plt.pause(0.01)

    print('Neat!')