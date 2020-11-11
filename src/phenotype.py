from typing import Tuple
from src.genotype import Genotype, NodeType


def relu(x: float) -> float:
    if x < 0:
        return 0
    else:
        return x


class Phenotype:

    node_inputs: "dict[int, float]"
    node_activations: "dict[int, float]"
    connections: "dict[int, list[Tuple[int, float, bool]]]"
    biases: "dict[int, float]"

    def __init__(self, genome: Genotype) -> None:

        # Dict of node input values indexed by node id
        self.node_inputs = {}

        # Dict of node activation values indexed by node id
        self.node_activations = {}

        # (activation values are the node inputs values with the activation function applied)

        # Dict of list tuples of nodes, weights and recurrent flag indexed by id of node they link to
        self.connections = {}

        # We must construct an ordered list of genes based on the genes order property
        node_genes = genome.node_genes.copy()
        node_genes.sort(key=lambda o: o.order)

        # List of nodes in the order they must be evaluated in (aside from input nodes)
        self.nodes = [
            node_gene.id for node_gene in node_genes if node_gene.type != NodeType.INPUT]

        self.output_nodes = [
            node_gene.id for node_gene in node_genes if node_gene.type == NodeType.OUTPUT]

        self.biases = dict([(node_gene.id, node_gene.bias)
                            for node_gene in node_genes])

        connection_genes = genome.connection_genes
        for conn in connection_genes:
            # Skip the disabled ones
            if (conn.enabled == False):
                continue
            self.connections.setdefault(conn.to, []).append(
                (conn.source, conn.weight, conn.recurrent))

    def calculate(self, inputs: "list[float]"):
        for i, activation in enumerate(inputs):
            self.node_activations[i] = activation

        for node in self.nodes:
            total = self.biases[node]
            for connection in self.connections.get(node, []):
                source, weight, rec = connection
                # Considers that on the first run recurrent connections will not have an activation
                total += self.node_activations.get(source, 0) * weight
            self.node_inputs[node] = total
            self.node_activations[node] = relu(total)

        return dict([
            (output_node, self.node_activations[output_node]) for output_node in self.output_nodes
        ])
