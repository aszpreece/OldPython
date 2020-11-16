from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.neat.phenotype import Phenotype
import unittest

# Set up genome for AND
genotype = Genotype()

node_genes = [
    # Input genes
    NodeGene(0, NodeType.BIAS),
    NodeGene(1, NodeType.INPUT),
    NodeGene(2, NodeType.INPUT),
    # Hidden genes
    NodeGene(3, NodeType.HIDDEN),
    NodeGene(4, NodeType.OUTPUT)
]

connection_genes = [
    ConnectionGene(0, 1, 3, 1),  # Weight from input 0
    ConnectionGene(1, 2, 3, 1),  # Weight from input 1
    ConnectionGene(2, 3, 4, 1),  # Weight to output
    ConnectionGene(3, 0, 3, -1)  # Weight from bias to 3
]

genotype.connection_genes = connection_genes
genotype.node_genes = node_genes


class TestAndNetwork(unittest.TestCase):

    def setUp(self):
        self.network = Phenotype(genotype)

    def test_and_result(self):
        inputs = [{0: 1.0, 1: 0.0, 2: 0.0}, {0: 1.0, 1: 0.0, 2: 1.0},
                  {0: 1.0, 1: 1.0, 2: 0.0}, {0: 1.0, 1: 1.0, 2: 1.0}]
        results = [self.network.calculate(input) for input in inputs]
        self.assertListEqual(results, [{4: x} for x in [0, 0, 0, 1]])

    def test_and_node_inputs(self):
        inputs = [{0: 1.0, 1: 0.0, 2: 0.0}, {0: 1.0, 1: 0.0, 2: 1.0},
                  {0: 1.0, 1: 1.0, 2: 0.0}, {0: 1.0, 1: 1.0, 2: 1.0}]
        for input in inputs:
            self.network.calculate(input)
            node_inputs = self.network.node_inputs
            expected = input[1] + input[2] + (input[0] * - 1)
            self.assertDictEqual(node_inputs,
                                 {
                                     3: expected,
                                     4: input[1] and input[2]
                                 })

    def test_and_activations(self):
        inputs = [{0: 1.0, 1: 0.0, 2: 0.0}, {0: 1.0, 1: 0.0, 2: 1.0},
                  {0: 1.0, 1: 1.0, 2: 0.0}, {0: 1.0, 1: 1.0, 2: 1.0}]
        for input in inputs:
            result = self.network.calculate(input)
            activations = self.network.node_activations
            expected = input[1] and input[2]
            print(activations)
            self.assertDictEqual(activations,
                                 {0: input[0], 1: input[1], 2: input[2], 3: expected, 4: expected})
