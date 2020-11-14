from typing import Callable, Dict, List, Optional, Tuple, TypeVar
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType
from random import Random


class NEAT:

    GT = TypeVar('GT')

    weight_perturb_scale: float
    prob_perturbing_weights: float
    new_weight_variance: float

    node_innovation_number: int
    connection_innovation_number: int

    # CONNECTION_INNOV_ID -> (NEW_NODE_INNOV_ID, FROM_INNOV_ID, TO_INNOV_ID)
    split_signatures: Dict[int, Tuple[int, int, int]]
    # (FROM_NODE, TO_NODE) -> INNOV_ID
    new_conn_signatures: Dict[Tuple[int, int], int]

    population: List[Genotype]
    fitness_function: Callable[[Genotype], float]

    def __init__(self, base_genotype: Genotype) -> None:
        self.weight_perturb_scale = 1.0
        self.prob_perturbing_weights = 0.1
        self.new_weight_variance = 1.5

        self.node_innovation_number = base_genotype.node_innov_start
        self.connection_innovation_number = base_genotype.conn_innov_start

        self.split_signatures = {}
        self.new_conn_signatures = {}

        self.mutator_operators = [
            self.weight_mutate,
            self.split_connection_mutate,
            self.add_connection_mutate
        ]

        self.split_signatures

        # TODO set initial innovation number

    def get_next_node_innov_num(self):
        self.node_innovation_number += 1
        return self.node_innovation_number

    def get_next_conn_innov_num(self):
        self.connection_innovation_number += 1
        return self.connection_innovation_number

    def mutate(self):
        pass

    def weight_mutate(self, genotype: Genotype, random: Random) -> None:
        """Given a genotype, mutate each weight.
        Weights have a chance of (1-self.chance_to_assign_random_weight) to have their weights perturbed by a scale of self.weight_perturb_scale.
        Weights have a chance of self.weight_perturb_scale to have their weight set to a random value.

        Args:
            genotype (Genotype): The genotype to mutate.
            random (Random): Instance of random to use.
        """

        for connection_gene in genotype.connection_genes:

            if random.uniform(0, 1) < self.prob_perturbing_weights:
                # Perturb the weights

                connection_gene.weight += (random.random() * 2.0 - 1.0) * \
                    self.weight_perturb_scale
            else:
                # Assign a new random from a normal distribution
                connection_gene.weight = random.normalvariate(
                    0, self.new_weight_variance)

    def split_connection_mutate(self, genotype: Genotype, random: Random) -> None:
        """Given a genotype, split a random connection and add an intermediate node.

        The weight of the connection between the original source node and the new will be the same as the connection we are splitting.
        The connection from the new node to the original from node will have the value 1.
        The original connection will be disabled.

        Args:
            genotype (Genotype): The genotype to mutate.
            random (Random): Instance of random to use.
        """

        # Decide on the connection to split

        # Fix: no longer tries to split disabled genes
        length = len(list(filter(lambda conn: conn.enabled,
                                 genotype.connection_genes)))

        index = random.randrange(0, length)

        # Disable the current connection
        originalConnection = genotype.connection_genes[index]
        originalConnection.enabled = False

        # See if this mutation has arisen in this generation and if so use the innovation ids from that mutation
        innovation_ids_tuple = self.split_signatures.get(
            originalConnection.innov_id)

        node_innov_id = None
        from_innov_id = None
        to_innov_id = None

        if not innovation_ids_tuple == None:
            node_innov_id, from_innov_id, to_innov_id = innovation_ids_tuple
        else:
            node_innov_id = self.get_next_node_innov_num()
            from_innov_id = self.get_next_conn_innov_num()
            to_innov_id = self.get_next_conn_innov_num()
            # Post the created innovation numbers as a tuple
            self.split_signatures[originalConnection.innov_id] = (
                node_innov_id, from_innov_id, to_innov_id)

        # Create a new node with a the innovation number
        genotype.node_genes.append(NodeGene(node_innov_id,
                                            NodeType.HIDDEN, bias=0))

        # New connection from old source to new node with weight of 1.0 to reduce impact
        genotype.connection_genes.append(ConnectionGene(
            from_innov_id, originalConnection.source, node_innov_id, 1.0))

        # New connection from new node to old to. Weight is that of the old connection
        genotype.connection_genes.append(ConnectionGene(
            to_innov_id, node_innov_id, originalConnection.to, originalConnection.weight))

    def add_connection_mutate(self, genotype: Genotype, random: Random) -> None:
        """Given a genotype, add a connection between two randomly selected previously unconnected nodes.
        The new connection will have a weight of 1.

        Args:
            genotype (Genotype): The genotype to mutate.
            random (Random): Instance of random to use.
        """

        # Shuffle two copies of the list of nodes. We can run through the first and attempt to pair it with a node from the second

        indexes = list(range(len(genotype.node_genes)))
        random.shuffle(indexes)

        # Dictionaries guarantee preservation of insertion order.
        firstList = dict((i, None) for i in indexes)

        random.shuffle(indexes)

        # We cannot connect 'to' input nodes so we should ignore them
        secondList = dict(
            (i, None) for i in indexes if genotype.node_genes[i].type != NodeType.INPUT)

        # The pair we have found
        pair: "Optional[Tuple[int, int]]" = None

        for first in firstList.keys():
            # We need to find all the connections that originate at the first node we have selected and log their 'to' node
            conns_from_first = set(
                conn.to for conn in genotype.connection_genes if conn.source == genotype.node_genes[first].innov_id)
            for second in secondList.keys():
                # Looping through the second list, check whether or not the second node is already connected to the first node (in the same direction)
                if not second in conns_from_first:
                    pair = (first, second)
                    break
            else:
                # If this node is connected to everything then we cannot connect it to a new node and we must select a new 'first node
                continue
            break

        # TODO
        # Unlikely, but we cannot do this mutation. How to handle? For now we can just do nothing
        # But we should probably mark this event somehow with a return value.
        if pair == None:
            return

        # Get new innov_id, either by checking if this mutation has happened before in this generation, or by getting a new one
        innov_id = self.new_conn_signatures.get(pair)
        if (innov_id == None):
            innov_id = self.get_next_conn_innov_num()

        genotype.connection_genes.append(
            ConnectionGene(innov_id, pair[0], pair[1], 1.0))
