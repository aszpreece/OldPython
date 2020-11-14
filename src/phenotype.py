from typing import Deque, List, Set, Tuple
from collections import deque
from src.genotype import ConnectionGene, Genotype, NodeType


def relu(x: float) -> float:
    if x < 0:
        return 0
    else:
        return x


def creates_cycle(connection: ConnectionGene, conn_dict: "dict[int, list[Tuple[int, float, int]]]", recurrent_connections: Set[int]) -> bool:

    if (connection.source == connection.to):
        return True

    visited_set: Set[int] = set()
    stack: Deque[int] = deque()

    stack.append(connection.source)

    target = connection.to

    # Figure out if there is a cycle by traversing the neuron connections
    # in reverse starting from the node this connection connects 'from' and attempt to find
    # a route back to it whilst avoiding previously introduced recurrent connections
    while (len(stack) != 0):
        node = stack.pop()
        visited_set.add(node)

        for source, _, innov_id in conn_dict.get(node, []):
            # Avoid recurrent connections
            if innov_id in recurrent_connections:
                continue
            # Else, check if we have found the target
            if source == target:
                return True
            # Avoid nodes we have already visited
            if source in visited_set:
                continue

            stack.append(source)

    return False


def calculate_execution_order(input_node_ids: List[int], non_input_node_ids: List[int], recurrent_connections: Set[int], connections: "dict[int, list[Tuple[int, float, int]]]"):
    # For now, lets do the brute force approach and save the order we are able to do the nodes in
    # There is definitley a better way though
    order: List[int] = []
    activated_nodes: Set[int] = set(input_node_ids)

    nodes_to_activate = set(non_input_node_ids)

    # Loop while there are still nodes that need to be activated
    while len(activated_nodes) != len(input_node_ids) + len(non_input_node_ids):
        # Track the nodes we activate on this iteration
        nodes_activated_iter = set()

        for node in nodes_to_activate:
            # For every connection this node has to it (unless it is recurrent)
            # If the node that the connection is sourced from is not activated
            # then we cannot activate either so skip

            for source, _, innov_id in connections[node]:
                if (not innov_id in recurrent_connections) and (not source in activated_nodes):
                    break
            else:
                # So we don't loop over again
                nodes_activated_iter.add(node)
                # Mark our node as activated
                activated_nodes.add(node)
                # Add this to our order as it can be activated
                order.append(node)
        if len(nodes_activated_iter) == 0:
            raise Exception(
                'No new nodes found to activate. This is either because of a glitch or the input data being corrupted')
        nodes_to_activate -= nodes_activated_iter
    return order


class Phenotype:

    node_inputs: "dict[int, float]"
    node_activations: "dict[int, float]"
    connections: "dict[int, list[Tuple[int, float, int]]]"
    biases: "dict[int, float]"
    recurrent_connections: Set[int]
    recurrent_nodes: Set[int]

    def __init__(self, genome: Genotype) -> None:

        # Dict of node activation values indexed by node id
        # (activation values are the node inputs values with the activation function applied)
        self.node_activations = {}

        # Dict of list of pairs of nodes and weights indexed by id of node they link *to*
        self.connections = {}

        # Set of innovation ids of the recurrent connections
        self.recurrent_connections = set()

        self.recurrent_nodes = set()

        # Dict of node input values indexed by node id
        self.node_inputs = {}

        # Array of the input nodes
        self.input_nodes = [
            node_gene.innov_id for node_gene in genome.node_genes if node_gene.type == NodeType.INPUT]

        # List of non input nodes
        self.nodes = [
            node_gene.innov_id for node_gene in genome.node_genes if node_gene.type != NodeType.INPUT]

        # List of output nodes
        self.output_nodes = [
            node_gene.innov_id for node_gene in genome.node_genes if node_gene.type == NodeType.OUTPUT]

        self.biases = dict([(node_gene.innov_id, node_gene.bias)
                            for node_gene in genome.node_genes])

        # Calculate an execution plan for the neural network.
        # We need to figure out *an* order we can calculate the nodes in.

        # Recurrent connections are *implied* by the ordering of the connection genes in the genome.
        # So we just need to check for cycles (ignoring any previously added recurrent connections)
        # when we add a new connection!

        for conn in genome.connection_genes:
            # Skip the disabled ones
            if conn.enabled == False:
                continue
            # If the connection causes a cycle, mark it as recurrent
            if creates_cycle(conn, self.connections, self.recurrent_connections):
                self.recurrent_connections.add(conn.innov_id)
                self.recurrent_nodes.add(conn.source)
            self.connections.setdefault(conn.to, []).append(
                (conn.source, conn.weight, conn.innov_id))

        # After this, we need to calculate our execution plan
        self.nodes = calculate_execution_order(
            self.input_nodes, self.nodes, self.recurrent_connections, self.connections)

    def calculate(self, inputs: "dict[int, float]"):

        recurrent_node_activations = dict()
        # Save the activations for the recurrent connections from the previous execution
        for id in self.recurrent_nodes:
            recurrent_node_activations[id] = self.node_activations.get(id,0)

        # Initialize the input nodes with the given activations
        for key, activation in inputs.items():
            self.node_activations[key] = activation

        for node in self.nodes:
            total = self.biases[node]
            for connection in self.connections.get(node, []):
                source, weight, innov_id = connection
                # If the connection has been marked as a recurrent connection fetch the val from the previous execution
                if innov_id in self.recurrent_connections:
                    total += recurrent_node_activations.get(source, 0) * weight
                # Else we can get it from our current array
                else:
                    total += self.node_activations[source] * weight

            self.node_inputs[node] = total
            self.node_activations[node] = relu(total)

        return dict([
            (output_node, self.node_activations[output_node]) for output_node in self.output_nodes
        ])
