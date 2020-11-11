
import unittest
from src.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.phenotype import Phenotype


class TestComplexRecurrent(unittest.TestCase):

    def setUp(self):
        self.genotype = Genotype()

        self.node_genes = [
            # Input genes
            NodeGene(NodeType.INPUT, 0.1, id=0),
            NodeGene(NodeType.INPUT, 0.1, id=1),
            NodeGene(NodeType.INPUT, 0.1, id=2),

            # Hidden genes
            NodeGene(NodeType.HIDDEN, 0.5, bias=0, id=3),
            NodeGene(NodeType.HIDDEN, 0.51, bias=0, id=4),

            # Output genes
            NodeGene(NodeType.OUTPUT, 1, id=5)
        ]

        self.connection_genes = [
            # Input connections
            ConnectionGene(0, 3, 0.5, 1),
            ConnectionGene(1, 3, 0.5, 2),
            ConnectionGene(1, 4, 2, 3),
            ConnectionGene(2, 4, 1.5, 3),
            # Hidden connection
            ConnectionGene(3, 4, 1, 3),
            # The recurrent connection from 4 to 3
            ConnectionGene(4, 3, 0.25, 3),
            # Hidden to output
            ConnectionGene(3, 5, 1, 3),
            ConnectionGene(4, 5, 1, 3),
            # The recurrent connection from 5 to 3
            ConnectionGene(4, 3, -0.1, 3),
        ]

        self.genotype.connection_genes = self.connection_genes
        self.genotype.node_genes = self.node_genes
        self.network = Phenotype(self.genotype)

    def test_output(self):
        result = self.network.calculate([1, 2, 3])
        self.assertEqual(result[5], 11.5)
        result = self.network.calculate([1, 2, 3])
        self.assertEqual(result[5], 14.5)
        result = self.network.calculate([1, 2, 3])
        self.assertEqual(result[5], 14.95)
