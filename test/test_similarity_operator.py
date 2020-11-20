from src.neat.neat import NEAT
from src.neat.helper import compare_connection_genes, compare_node_genes
import unittest
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.neat.phenotype import Phenotype


class TestSimilarityOperator(unittest.TestCase):

    def test_correct_connections(self):
        gen1 = Genotype()
        gen2 = Genotype()

        gen1.connection_genes = [
            ConnectionGene(1, 1, 1, 1),
            ConnectionGene(2, 1, 1, 1),
            ConnectionGene(3, 1, 1, 1),
            ConnectionGene(4, 1, 1, 1),
            ConnectionGene(5, 1, 1, 1)
        ]

        gen2.connection_genes = [
            # Three disjoint
            ConnectionGene(4, 1, 1, 1),
            ConnectionGene(5, 1, 1, 1),
            # These Four are excess
            ConnectionGene(10, 1, 1, 1),
            ConnectionGene(11, 1, 1, 1),
            ConnectionGene(12, 1, 1, 1),
            ConnectionGene(13, 1, 1, 1),

        ]

        disjoint_conn, excess_conn, average_weight = compare_connection_genes(
            gen1.connection_genes, gen2.connection_genes)
        self.assertEqual(average_weight, 0)
        self.assertEqual(disjoint_conn, 3)
        self.assertEqual(excess_conn, 4)

    def test_correct_nodes(self):
        gen1 = Genotype()
        gen2 = Genotype()

        gen1.node_genes = [
            NodeGene(1, NodeType.OUTPUT),
            NodeGene(2, NodeType.OUTPUT),
            NodeGene(3, NodeType.OUTPUT),
            NodeGene(4, NodeType.OUTPUT),
            NodeGene(5, NodeType.OUTPUT)
        ]

        gen2.node_genes = [
            NodeGene(1, NodeType.OUTPUT),
            # Two disjoint disjoint
            NodeGene(4, NodeType.OUTPUT),
            NodeGene(5, NodeType.OUTPUT),
            # Three excess
            NodeGene(6, NodeType.OUTPUT),
            NodeGene(7, NodeType.OUTPUT),
            NodeGene(8, NodeType.OUTPUT)

        ]

        disjoint_nodes, excess_nodes = compare_node_genes(
            gen1.node_genes, gen2.node_genes)
        self.assertEqual(disjoint_nodes, 2)
        self.assertEqual(excess_nodes, 3)

    def test_correct_weight_average(self):

        gen1 = Genotype()
        gen2 = Genotype()

        gen1.connection_genes = [
            ConnectionGene(1, 1, 1, 1),
            ConnectionGene(2, 1, 1, 1),
            ConnectionGene(3, 1, 1, 1),
            ConnectionGene(4, 1, 1, 10),
            ConnectionGene(5, 1, 1, 20)
        ]

        gen2.connection_genes = [
            # Three disjoint
            ConnectionGene(4, 1, 1, 1),
            ConnectionGene(5, 1, 1, 1),
            # These Four are excess
            ConnectionGene(10, 1, 1, 1),
            ConnectionGene(11, 1, 1, 1),
            ConnectionGene(12, 1, 1, 1),
            ConnectionGene(13, 1, 1, 1),

        ]

        disjoint_conn, excess_conn, average_weight = compare_connection_genes(
            gen1.connection_genes, gen2.connection_genes)
        self.assertEqual(average_weight, (9+19)/2)
        self.assertEqual(disjoint_conn, 3)
        self.assertEqual(excess_conn, 4)

    def test_correct_similarity(self):

        gen1 = Genotype()
        gen2 = Genotype()

        gen1.connection_genes = [
            ConnectionGene(1, 1, 1, 1),
            ConnectionGene(2, 1, 1, 1),
            ConnectionGene(3, 1, 1, 1),
            ConnectionGene(4, 1, 1, 10),
            ConnectionGene(5, 1, 1, 20)
        ]

        gen2.connection_genes = [
            # Three disjoint
            ConnectionGene(4, 1, 1, 1),
            ConnectionGene(5, 1, 1, 1),
            # These Four are excess
            ConnectionGene(10, 1, 1, 1),
            ConnectionGene(11, 1, 1, 1),
            ConnectionGene(12, 1, 1, 1),
            ConnectionGene(13, 1, 1, 1),

        ]

        gen1.node_genes = [
            NodeGene(1, NodeType.OUTPUT),
            NodeGene(2, NodeType.OUTPUT),
            NodeGene(3, NodeType.OUTPUT),
            NodeGene(4, NodeType.OUTPUT),
            NodeGene(5, NodeType.OUTPUT)
        ]

        gen2.node_genes = [
            NodeGene(1, NodeType.OUTPUT),
            # Two disjoint
            NodeGene(4, NodeType.OUTPUT),
            NodeGene(5, NodeType.OUTPUT),
            # Three excess
            NodeGene(6, NodeType.OUTPUT),
            NodeGene(7, NodeType.OUTPUT),
            NodeGene(8, NodeType.OUTPUT),
            NodeGene(9, NodeType.OUTPUT)
        ]
        disjoint_conn, excess_conn, average_weight = compare_connection_genes(
            gen1.connection_genes, gen2.connection_genes)
        self.assertEqual(average_weight, (9+19)/2)
        self.assertEqual(disjoint_conn, 3)
        self.assertEqual(excess_conn, 4)

        disjoint_nodes, excess_nodes = compare_node_genes(
            gen1.node_genes, gen2.node_genes)
        self.assertEqual(disjoint_nodes, 2)
        self.assertEqual(excess_nodes, 4)

        neat = NEAT(gen1, 10, lambda x: 1.0)

        similarity = neat.similarity_operator(gen1, gen2)

        longest_genome_len = 13
        expected = ((9 + 19)/2) * neat.sim_weight_diff_weight + \
            (5 * neat.sim_disjoint_weight) / longest_genome_len + \
            (8 * neat.sim_excess_weight) / longest_genome_len

        self.assertAlmostEqual(similarity, expected, 6)
