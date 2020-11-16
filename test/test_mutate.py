
from random import Random
import unittest
import mock

from src.neat.mutators import NEAT
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType


class TestMutate(unittest.TestCase):

    def test_weight_mutate(self):
        genome = Genotype()
        genome.connection_genes = [
            ConnectionGene(1, 9, 5, 0.1),
            ConnectionGene(2, 90, 55, 2.0)
        ]

        # Doesn't matter this arg shouldn't be used yet
        neat = NEAT(genome, 100, lambda x: 1)
        neat.prob_perturbing_weights = 0.1
        neat.weight_perturb_scale = 1.0
        neat.new_weight_variance = 1.5

        random = Random(100000)

        # This should trigger the weight to be perturbed
        first_call = random.uniform(0, 1)  # 0.09340878192995006
        # Perturbing random
        second_call = random.random()  # 0.787554696332499
        # This should trigger the weight to be completely reset
        third_call = random.uniform(0, 1)  # 0.6912020474815175
        # This should be the new weight
        fourth_call = random.normalvariate(0, 1.5)  # 0.6723792860870663

        # Reset random
        random = Random(100000)
        neat.weight_mutate(genome, random)

        w1 = genome.connection_genes[0].weight
        expected = 0.1 + (second_call * 2.0 - 1.0) * neat.weight_perturb_scale
        self.assertAlmostEquals(w1, expected, 5)

        w2 = genome.connection_genes[1].weight
        expected = fourth_call
        self.assertAlmostEquals(w2, expected, 5)

    def test_split_connection_mutate(self):
        genome = Genotype()
        genome.connection_genes = [
            ConnectionGene(1, 9, 5, 0.1),
            ConnectionGene(2, 90, 55, 2.0)
        ]

        genome.conn_innov_start = 3

        # Doesn't matter this arg shouldn't be used yet
        neat = NEAT(genome, 100, lambda x: 1)

        # Seed so we get same results
        random = Random(1001)
        neat.split_connection_mutate(genome, random)

        # Assert we have a new node gene
        self.assertEqual(len(genome.node_genes), 1)

        # Assert we have two new connection genes
        self.assertEqual(len(genome.connection_genes), 4)

        # The connection that was split
        split = genome.connection_genes[0]
        # Assert the first connection is disabled
        self.assertFalse(split.enabled)

        # Assert there is a connection from 9 to 1 and from 1 to 5
        # first conn
        nine_to_one = list(filter(lambda conn: (
            conn.source == 9 and conn.to == 1), genome.connection_genes))
        self.assertEqual(len(nine_to_one), 1)

        one_to_five = list(filter(lambda conn: (
            conn.source == 1 and conn.to == 5), genome.connection_genes))
        self.assertEqual(len(one_to_five), 1)

        # Assert weights were set correctly
        self.assertEqual(nine_to_one[0].weight, 1)
        self.assertEqual(one_to_five[0].weight, 0.1)

        # Now to test that the mutator will not try to split the same connection again
        random = Random(1001)
        neat.split_connection_mutate(genome, random)

        # I.e these connections should not have been created again
        nine_to_one_two = list(filter(lambda conn: (
            conn.source == 9 and conn.to == 1), genome.connection_genes))
        self.assertEqual(len(nine_to_one_two), 1)

        one_to_five_two = list(filter(lambda conn: (
            conn.source == 1 and conn.to == 5), genome.connection_genes))
        self.assertEqual(len(one_to_five_two), 1)

        # TODO improve this but i am going to move on now

    def test_split_connection_mutate_uses_old_number(self):

        genome1 = Genotype()
        genome1.connection_genes = [
            ConnectionGene(1, 9, 5, 0.1),
            ConnectionGene(2, 90, 55, 2.0)
        ]
        genome1.conn_innov_start = 3
        genome1.node_innov_start = 10

        # Doesn't matter this arg shouldn't be used yet
        neat = NEAT(genome1, 100, lambda x: 1)

        # Seed so we get same results
        random = Random(1001)
        neat.split_connection_mutate(genome1, random)
        # Assert we have a new node gene
        self.assertEqual(len(genome1.node_genes), 1)
        # Assert we have two new connection genes
        self.assertEqual(len(genome1.connection_genes), 4)
        # The connection that was split
        split = genome1.connection_genes[0]
        # Assert the first connection is disabled
        self.assertFalse(split.enabled)

        genome2 = Genotype()
        genome2.connection_genes = [
            ConnectionGene(1, 9, 5, 0.1),
            ConnectionGene(2, 90, 55, 2.0)
        ]

        # Change this so we definitley know it got the new innov ids from the hashmap
        neat.node_innovation_number = 1010
        neat.connection_innovation_number = 2000

        # Seed so we get same results
        random = Random(1001)
        neat.split_connection_mutate(genome2, random)

        # Check the three new genes that have been added
        new_from = genome2.connection_genes[2]
        new_to = genome2.connection_genes[3]
        new_node = genome2.node_genes[0]

        # Check they are what we would expect
        self.assertEqual(new_from.innov_id, 4)
        self.assertEqual(new_to.innov_id, 5)
        self.assertEqual(new_node.innov_id, 11)

    def test_add_connection_mutate_ignores_input_nodes(self):
        genome = Genotype()
        genome.connection_genes = []
        genome.node_genes = [
            NodeGene(10, NodeType.INPUT),
            NodeGene(20, NodeType.INPUT)
        ]

        genome.conn_innov_start = 10

        # Doesn't matter this arg shouldn't be used yet
        neat = NEAT(genome, 100, lambda x: 1)
        random = Random(1001)

        # This shouldn't be able to do anything
        neat.add_connection_mutate(genome, random)

        self.assertEqual(len(genome.connection_genes), 0)

    def test_add_connection_mutate_ignores_current_conns(self):
        genome = Genotype()
        genome.connection_genes = [
            ConnectionGene(5, 10, 20, 0.1),
            ConnectionGene(6, 20, 10, 2.0),
            ConnectionGene(7, 10, 10, 2.0),
            ConnectionGene(8, 20, 20, 2.0)

        ]
        genome.node_genes = [
            NodeGene(10, NodeType.HIDDEN),
            NodeGene(20, NodeType.HIDDEN)
        ]

        genome.conn_innov_start = 10

        # Doesn't matter this arg shouldn't be used yet
        neat = NEAT(genome, 100, lambda x: 1)
        random = Random(123)

        # This shouldn't be able to do anything because the network is fully connected
        neat.add_connection_mutate(genome, random)

        self.assertEqual(len(genome.connection_genes), 4)

    def test_add_connection_mutate_makes_connection(self):
        genome1 = Genotype()
        connection_genes = [
            ConnectionGene(1011, 10, 20, 0.1),
        ]
        node_genes = [
            NodeGene(20, NodeType.HIDDEN),
            NodeGene(10, NodeType.HIDDEN)
        ]

        genome1.conn_innov_start = 10
        genome1.connection_genes = connection_genes.copy()
        genome1.node_genes = node_genes.copy()

        # Doesn't matter this arg shouldn't be used yet
        neat = NEAT(genome1, 100, lambda x: 1)
        random = Random(1001)

        # This should be able to make a connection between
        neat.add_connection_mutate(genome1, random)

        self.assertEqual(len(genome1.connection_genes), 2)

        # Set up another test genome
        genome2 = Genotype()
        genome2.conn_innov_start = 10
        genome2.connection_genes = connection_genes.copy()
        genome2.node_genes = node_genes.copy()
        random = Random(1001)

        # This should be able to make the same connection between 1 and 1, but it should use the same innovation number as the previous mutation
        neat.add_connection_mutate(genome2, random)

        innov_id = genome2.connection_genes[1].innov_id
        self.assertEqual(innov_id, 11)
        self.assertEqual(len(genome2.connection_genes), 2)

    def test_add_connection_mutate_re_enables_connection(self):
        genome = Genotype()
        genome.connection_genes = [
            ConnectionGene(5, 10, 20, 0.1),
            ConnectionGene(6, 20, 10, 2.0),
            ConnectionGene(7, 10, 10, 2.0),
            ConnectionGene(8, 20, 20, 2.0, enabled=False)

        ]
        genome.node_genes = [
            NodeGene(10, NodeType.HIDDEN),
            NodeGene(20, NodeType.HIDDEN)
        ]

        genome.conn_innov_start = 10

        # Doesn't matter this arg shouldn't be used yet
        neat = NEAT(genome, 100, lambda x: 1)
        random = Random(123)

        # The only thing this can do is re-enable the disabled connection between 20 and 20
        neat.add_connection_mutate(genome, random)

        self.assertEqual(len(genome.connection_genes), 4)
        self.assertTrue(genome.connection_genes[3].enabled)
