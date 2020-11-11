
from src.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from src.phenotype import Phenotype

genotype = Genotype()

node_genes = []
# Input genes
node_genes.extend([
    NodeGene(i, NodeType.INPUT, 0.1) for i in range(2)
])

# Hidden genes
node_genes.extend([
    NodeGene(2, NodeType.HIDDEN, 0.5, bias=-1)
])

# Output genes
node_genes.extend([
    NodeGene(3, NodeType.OUTPUT, 1)
])

connection_genes = [
    ConnectionGene(0, 2, 1, 1),  # Weight from input 0
    ConnectionGene(1, 2, 1, 2),  # Weight from input 1
    ConnectionGene(2, 3, 1, 3)  # Weight to output
]


genotype.connection_genes = connection_genes
genotype.node_genes = node_genes

network = Phenotype(genotype)

inputs = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
results = [network.calculate(input) for input in inputs]
print(results)

# print(result)

# print('ACTIVATIONS')
# print(network.node_activations)
# print('')
# print('INPUTS')
# print(network.node_inputs)

# CreateGraph(genotype)
