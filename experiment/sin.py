
from matplotlib.pyplot import axis
from experiment.run_experiment import train_neat
import random
import math
from typing import List, Tuple

from matplotlib import pyplot as plt
from src.neat.neat import NEAT
from src.neat.phenotype import Phenotype
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.ui.graphnetwork import create_graph
import numpy as np

import logging
from typing import List, Tuple

logging.basicConfig(level=logging.NOTSET)

base_genotype = Genotype()

base_genotype.node_genes = [
    NodeGene(0, NodeType.BIAS),
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
    return 2 * (s - 0.5)


plt.ion()
fig, axarr = plt.subplots(2, figsize=(6, 8))
fig.show()


def plot_sin(neat: NEAT):

    def plot_sin(genotype, axis):
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
        axis.text(0.1, 0.9, f'{genotype.species.species_id}', fontsize=12)

    plot_sin(neat.population.best_individual, axarr[0])
    plot_sin(random.choice(neat.population.population), axarr[1])


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

    return 1 / (((1/len(test_cases)) * score))


train_neat(base_genotype, fitness_function_sin, plot_sin)
