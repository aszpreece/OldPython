import unittest
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.neat.phenotype import Phenotype


class TestSimilarityOperator(unittest.TestCase):

    def test_correct_under_20(self):
        gen1 = Genotype()
        gen2 = Genotype()

        gen1.connection_genes = [
            ConnectionGene(1, 1, 1, 1),
            ConnectionGene(2, 1, 1, 1),
            ConnectionGene(3, 1, 1, 1),
            ConnectionGene(4, 1, 1, 1),
            ConnectionGene(5, 1, 1, 1)
        ]

        gen1.connection_genes = [
            # Two disjoint
            ConnectionGene(3, 1, 1, 1),
            ConnectionGene(4, 1, 1, 1),
            ConnectionGene(5, 1, 1, 1),
            # These two are excess
            ConnectionGene(10, 1, 1, 1),
            ConnectionGene(11, 1, 1, 1),
        ]
        gen2.node_genes = [
            NodeGene(1, NodeType.OUTPUT),
            NodeGene(1, NodeType.OUTPUT),
            NodeGene(1, NodeType.OUTPUT),
            NodeGene(1, NodeType.OUTPUT),
            NodeGene(1, NodeType.OUTPUT)
        ]
