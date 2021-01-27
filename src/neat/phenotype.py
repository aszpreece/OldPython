
import math
from collections import deque
from src.neat.node_type import NodeType
from typing import Deque, Dict, List, Set, Tuple
# from src.neat.genotype import ConnectionGene, Genotype, NodeType


class Phenotype:

    node_inputs: "dict[int, float]"
    node_activations: "dict[int, float]"
    connections: "dict[int, list[Tuple[int, float, int]]]"

    def __init__(self, genome) -> None:

        # Dict of node activation values indexed by node id
        # (activation values are the node inputs values with the activation function applied)
        self.node_activations = {}

        # Dict of list of pairs of nodes and weights indexed by id of node they link *to*
        self.connections = {}

        # Array of the input/bias nodes
        self.input_nodes = [
            node_gene.innov_id for node_gene in genome.node_genes if node_gene.type == NodeType.INPUT or node_gene.type == NodeType.BIAS]

        # List of non input/bias nodes
        self.nodes = [
            (node_gene.innov_id, node_gene.activation_func) for node_gene in genome.node_genes if node_gene.type != NodeType.INPUT and node_gene.type != NodeType.BIAS]

        # List of output nodes
        self.output_nodes = [
            node_gene.innov_id for node_gene in genome.node_genes if node_gene.type == NodeType.OUTPUT]

        for conn in genome.connection_genes:
            # Skip the disabled ones
            if conn.enabled == False:
                continue
            self.connections.setdefault(conn.to, []).append(
                (conn.source, conn.weight, conn.innov_id))

        # Set the genome's phenotype
        genome.phenotype = self

    def calculate(self, inputs: "dict[int, float]"):
        """Calculate a cycle of this network

        Args:
            inputs (dict[int, float]): A dict of inputs where the key of the entry corresponds to the id of the input node.

        Returns:
            dict[int, float]: A dictionary of the output nodes and their activation values
        """
        new_activations = {}

        # Initialize the input nodes with the given activations
        for key, activation in inputs.items():
            new_activations[key] = activation
        
        for node_id, activation_func in self.nodes:
            total = 0
            for connection in self.connections.get(node_id, []):
                source, weight, innov_id = connection
                total += self.node_activations.get(source, 0) * weight

            new_activations[node_id] = activation_func(total)

        self.node_activations = new_activations

        return dict([
            (output_node, self.node_activations[output_node]) for output_node in self.output_nodes
        ])
