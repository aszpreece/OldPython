
from random import Random
import unittest
import mock

from src.neat.mutators import NEAT
from src.neat.genotype import ConnectionGene, Genotype


class TestMutate(unittest.TestCase):

    def test_weight_mutate(self):
        genome = Genotype()
        genome.connection_genes = [
            ConnectionGene(1, 9, 5, 0.1),
            ConnectionGene(2, 90, 55, 2.0)
        ]

        # Doesn't matter this arg shouldn't be used yet
        neat = NEAT(genome)
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
        neat = NEAT(genome)

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

        # Now to test that the mutator will not try to add back in a connection that already exists
        random = Random(1001)
        neat.split_connection_mutate(genome, random)

        # I.e these connections should not have been created again
        nine_to_one_two = list(filter(lambda conn: (
            conn.source == 9 and conn.to == 1), genome.connection_genes))
        self.assertEqual(len(nine_to_one_two), 1)

        one_to_five_two = list(filter(lambda conn: (
            conn.source == 1 and conn.to == 5), genome.connection_genes))
        self.assertEqual(len(one_to_five_two), 1)
