
import random
import math
from typing import List, Tuple

from matplotlib import pyplot as plt
from matplotlib.pyplot import title, xlabel, ylabel
from src.neat.mutators import NEAT
from src.neat.phenotype import Phenotype
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.ui.graphnetwork import create_graph
import numpy as np

import logging
from typing import List, Tuple


logging.basicConfig(level=logging.NOTSET)


def train_xor():

    base_genotype = Genotype()

    base_genotype.node_genes = [
        NodeGene(0, NodeType.BIAS),
        NodeGene(1, NodeType.INPUT),
        NodeGene(2, NodeType.INPUT),
        NodeGene(3, NodeType.OUTPUT)
    ]

    base_genotype.connection_genes = [
        ConnectionGene(1, 1, 3, 1.0),
        ConnectionGene(2, 2, 3, 1.0)
    ]

    base_genotype.conn_innov_start = 2
    base_genotype.node_innov_start = 3

    def fitness_function_xor(genotype: Genotype) -> float:

        score: float = 0

        test_cases: List[Tuple[int, int, int]] = [
            (0, 0, 0),
            (1, 0, 1),
            (0, 1, 1),
            (1, 1, 0)
        ]
        phenotype = Phenotype(genotype)
        for ione, itwo, expected in test_cases:
            result = phenotype.calculate_no_rec({
                0: 1, 1: ione, 2: itwo
            })

            # Mean square error
            score += (result[3] - expected)**2

        return (1/len(test_cases)) * score

    train_neat(base_genotype, fitness_function_xor)


def train_sin():
    base_genotype = Genotype()

    base_genotype.node_genes = [
        NodeGene(0, NodeType.INPUT),
        NodeGene(1, NodeType.INPUT),
        NodeGene(2, NodeType.OUTPUT)
    ]

    base_genotype.connection_genes = [
        ConnectionGene(1, 1, 2, 1.0),
    ]

    base_genotype.conn_innov_start = 1
    base_genotype.node_innov_start = 2

    def radian_to_scalar(r):
        return r / (math.pi * 2)

    def scalar_to_output(s):
        return s - 1

    def plot_sin(genotype: Genotype, axis):
        phenotype = Phenotype(genotype)

        xs = []
        results = []
        expected = []
        for x in np.linspace(-1 * math.pi, 1 * math.pi, 100):
            xs.append(x)
            result = phenotype.calculate_no_rec({
                0: 1, 1: radian_to_scalar(x)  # Normalize input
            })[2]
            expected.append(math.sin(x))
            results.append(scalar_to_output(result))
        axis.clear()
        axis.set(title="Results",
                 xlabel='x (Radians)', ylabel='y')
        axis.plot(xs, expected)
        axis.plot(xs, results)
        axis.legend(["Expected", "Result"])

    def fitness_function_sin(genotype: Genotype) -> float:

        score: float = 0

        test_cases: List[Tuple[float, float]] = [
            (input, math.sin(input)) for input in np.linspace(-1 * math.pi, 1 * math.pi, 50)]

        phenotype = Phenotype(genotype)
        for x, expected in test_cases:
            result = phenotype.calculate_no_rec({
                0: 1, 1: radian_to_scalar(x)
            })[2]

            out = scalar_to_output(result)

            # Mean square error
            score += (out - expected)**2

        return (1/len(test_cases)) * score

    train_neat(base_genotype, fitness_function_sin, plot_sin)


def train_neat(base_genotype: Genotype, fitness_func, result_func=lambda genotype, figure: None):

    neat = NEAT(base_genotype, 150, fitness_func)

    # neat.percentage_top_networks_passed_on = 0.2
    # neat.prob_to_split_connection = 0.2
    # neat.prob_to_connect_nodes = 0.3

    plt.ion()

    fig, axarr = plt.subplots(3, figsize=(6, 8))
    plt.subplots_adjust(wspace=0.5, hspace=1)
    fig.show()

    error = []
    complexity = []

    score = math.inf
    generation = 0
    old_score = -100
    while score > 0.002:
        generation += 1
        result = neat.run_generation()
        if result != None:
            score, index = result
            if old_score != score:
                print(f'Score for generation {generation} is {score}')

            solution = neat.population[index]

            old_score = score

            error.append(score)
            complexity.append(solution.get_complexity())

            axarr[0].clear()
            axarr[0].set(title="Loss",
                         xlabel='Generation', ylabel='Error')
            axarr[0].plot(error)

            axarr[1].clear()
            axarr[1].set(title="Complexity",
                         xlabel='Generation', ylabel='Count')
            axarr[1].plot(complexity)
            axarr[1].legend(["Nodes", "Connections", "Enabled Connections"])

            result_func(solution, axarr[2])

            fig.canvas.draw()
            plt.pause(0.01)

    print('Neat!')


train_sin()
