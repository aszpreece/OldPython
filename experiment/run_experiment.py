

from src.neat.neat_config import NeatConfig
from src.neat.neat import NEAT
import numpy as np

import logging
from typing import List, Tuple


def train_neat(fitness_func, config: NeatConfig, target_score = None, result_func=lambda neat: None, generations=None):

    neat = NEAT(config)

    # plt.ion()

    # fig, axarr = plt.subplots(3, figsize=(6, 8))
    # plt.subplots_adjust(wspace=0.5, hspace=1)
    # fig.show()

    error = []
    complexity = []
    species_count = []

    score = 0
    generation = 0
    old_score = 0

    while (target_score is None or score < target_score) and (generations is None or generation < generations):
        generation += 1
        logging.debug(f'=====Generation {generation}=====')
        solution = neat.run_generation()
        score = solution.fitness
        if solution != None:
            if old_score != score:
                print(f'Score for generation {generation} is {score}')

            neat.print_species()

            old_score = score

            error.append(score)
            complexity.append(solution.get_complexity())

            # axarr[0].clear()
            # axarr[0].set(title="Fitness",
            #              xlabel='Generation', ylabel='Fitness')
            # axarr[0].plot(error)

            # axarr[1].clear()
            # axarr[1].set(title="Complexity",
            #              xlabel='Generation', ylabel='Count')
            # axarr[1].plot(complexity)
            # axarr[1].legend(
            #     ["Nodes", "Connections", "Enabled Connections"])

            species_count.append(len(neat.species))

            # axarr[2].clear()
            # axarr[2].set(title="Species",
            #              xlabel='Generation', ylabel='Count')
            # axarr[2].plot(species_count)
            # axarr[2].legend(["Species"])

            result_func(neat)

            # fig.canvas.draw()
            # plt.pause(0.01)

    print(f'Generations: {generation}')

    return error, complexity, species_count

    


# 0:83.5
# 1:112.0
# 2:78.375
# 3:93.625
# 4:110.375
# 5:134.5
