import unittest
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType, relu
from src.neat.phenotype import Phenotype


class TestRecurrentSummer(unittest.TestCase):

    def setUp(self):
        # Set up genome for an adder that outputs the sum of all of
        # the positive inputs its been given so far

        self.genotype = Genotype()

        self.node_genes = [
            # Input genes
            NodeGene(0, NodeType.INPUT, activation_func=relu),
            # Hidden genes
            NodeGene(1, NodeType.HIDDEN, activation_func=relu),
            # Output genes
            NodeGene(2, NodeType.OUTPUT, activation_func=relu)
        ]

        self.connection_genes = [
            ConnectionGene(1, 0, 1, 1),  # Input to hidden
            ConnectionGene(2, 1, 1, 1, recurrent=True),  # Hidden to hidden (recurrent)
            ConnectionGene(3, 1, 2, 1)  # Hidden to output
        ]

        self.genotype.connection_genes = self.connection_genes
        self.genotype.node_genes = self.node_genes

        self.network = Phenotype(self.genotype)

    def test_summation(self):
        print(self.network.node_activations)
        result = self.network.calculate({0: 1})
        self.assertEqual(result[2], 0)

        result = self.network.calculate({0: 2})
        print(self.network.node_activations)

        self.assertEqual(result[2], 0)
        result = self.network.calculate({0: 10})
        self.assertEqual(result[2], 1)
        result = self.network.calculate({0: -10})
        self.assertEqual(result[2], 3)
        result = self.network.calculate({0: -10})
        self.assertEqual(result[2], 13)