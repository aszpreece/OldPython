from src.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.phenotype import Phenotype
import unittest

# Set up genome for AND
genotype = Genotype()

node_genes = []
# Input genes
node_genes.extend([
    NodeGene(NodeType.INPUT, 0.1, id=i) for i in range(2)
])

# Hidden genes
node_genes.extend([
    NodeGene(NodeType.HIDDEN, 0.5, bias=-1, id=2)
])

# Output genes
node_genes.extend([
    NodeGene(NodeType.OUTPUT, 1, id=3)
])

connection_genes = [
    ConnectionGene(0, 2, 1, 1),  # Weight from input 0
    ConnectionGene(1, 2, 1, 2),  # Weight from input 1
    ConnectionGene(2, 3, 1, 3)  # Weight to output
]


genotype.connection_genes = connection_genes
genotype.node_genes = node_genes


class TestAnd(unittest.TestCase):

    def setUp(self):
        self.network = Phenotype(genotype)

    def test_and_result(self):
        inputs = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        results = [self.network.calculate(input) for input in inputs]
        self.assertListEqual(results, [{3: x} for x in [0, 0, 0, 1]])

    def test_and_node_inputs(self):
        inputs = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        for input in inputs:
            self.network.calculate(input)
            node_inputs = self.network.node_inputs
            expected = input[0] + input[1] + self.network.biases[2]
            self.assertDictEqual(node_inputs,
                                 {
                                     2: expected,
                                     3: input[0] and input[1]
                                 })

    def test_and_activations(self):
        inputs = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        for input in inputs:
            result = self.network.calculate(input)
            activations = self.network.node_activations
            expected = input[0] and input[1]
            print(activations)
            self.assertDictEqual(activations,
                                 {0: input[0], 1: input[1], 2: expected, 3: expected})
