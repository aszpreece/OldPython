
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
