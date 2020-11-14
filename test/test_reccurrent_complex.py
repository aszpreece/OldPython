
import unittest
from src.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.phenotype import Phenotype


class TestComplexRecurrent(unittest.TestCase):

    def setUp(self):
        self.genotype = Genotype()

        self.node_genes = [
            # Input genes
            NodeGene(0, NodeType.INPUT),
            NodeGene(1, NodeType.INPUT),
            NodeGene(2, NodeType.INPUT),

            # Hidden genes
            NodeGene(3, NodeType.HIDDEN),
            NodeGene(4, NodeType.HIDDEN),

            # Output genes
            NodeGene(5, NodeType.OUTPUT)
        ]

        self.connection_genes = [
            # Input connections
            ConnectionGene(1, 0, 3, 0.5),
            ConnectionGene(2, 1, 3, 0.5),
            ConnectionGene(3, 1, 4, 2),
            ConnectionGene(4, 2, 4, 1.5),
            # Hidden connection
            ConnectionGene(5, 3, 4, 1),
            # The recurrent connection from 4 to 3
            ConnectionGene(6, 4, 3, 0.25),
            # Hidden to output
            ConnectionGene(7, 3, 5, 1),
            ConnectionGene(8, 4, 5, 1),
            # The recurrent connection from 5 to 3
            ConnectionGene(9, 4, 3, -0.1),
        ]

        self.genotype.connection_genes = self.connection_genes
        self.genotype.node_genes = self.node_genes
        self.network = Phenotype(self.genotype)

    def test_output(self):
        result = self.network.calculate({0: 1, 1: 2, 2: 3})
        self.assertEqual(result[5], 11.5)
        result = self.network.calculate({0: 1, 1: 2, 2: 3})
        self.assertEqual(result[5], 14.5)
        result = self.network.calculate({0: 1, 1: 2, 2: 3})
        self.assertEqual(result[5], 14.95)
