import unittest
from src.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.phenotype import Phenotype


class TestRecurrentSummer(unittest.TestCase):

    def setUp(self):
        # Set up genome for an adder that outputs the sum of all of
        # the positive inputs its been given so far

        self.genotype = Genotype()

        self.node_genes = [
            # Input genes
            NodeGene(NodeType.INPUT, 0.1, id=0),
            # Hidden genes
            NodeGene(NodeType.HIDDEN, 0.5, bias=0, id=1),
            # Output genes
            NodeGene(NodeType.OUTPUT, 1, id=2)
        ]

        self.connection_genes = [
            ConnectionGene(0, 1, 1, 1),  # Input to hidden
            ConnectionGene(1, 1, 1, 2),  # Hidden to hidden
            ConnectionGene(1, 2, 1, 3)  # Hidden to output
        ]

        self.genotype.connection_genes = self.connection_genes
        self.genotype.node_genes = self.node_genes

        self.network = Phenotype(self.genotype)

    def testOutput(self):
        result = self.network.calculate([1])
        self.assertEqual(result[2], 1)
        result = self.network.calculate([2])
        self.assertEqual(result[2], 3)
        result = self.network.calculate([10])
        self.assertEqual(result[2], 13)
        result = self.network.calculate([-10])
        self.assertEqual(result[2], 3)
