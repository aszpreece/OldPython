from typing import Callable, Generic, List, Optional, Set, Tuple, TypeVar
from src.genotype import Genotype, NodeGene, NodeType
# TODO Investigate whether or not this library will be 'random' enough
import random

GT = TypeVar('GT')

GeneticOperator = Callable[[GT], None]


class HyperParameters(Generic[GT]):
    """Container for hyperparameters.
    """
    weight_mutation_scale: float

    mutator_operators: List[GeneticOperator]

    def __init__(self) -> None:
        self.weight_mutation_scale = 1.0


class NEAT:

    hyper_params = HyperParameters()

    # Innovation ids for nodes and connections
    n_in_id = 0
    c_in_id = 0

    def weight_mutate(self, genotype: Genotype) -> None:
        """Given a genotype, mutate a random weight of a connection gene.

        Args:
            genotype (Genotype): The genotype to mutate.
        """

        length = len(genotype.connection_genes)
        index = random.randrange(0, length)
        gene = genotype.connection_genes[index]
        gene.weight += (random.random() * 2.0 - 1.0) * \
            hyper_params.weight_mutation_scale

    def split_connection_mutate(self, genotype: Genotype) -> None:
        """Given a genotype, split a random connection and add an intermediate node.

        The weight of the connection between the original source node and the new will be the same as the connection we are splitting.
        The connection from the new node to the original from node will have the value 1.
        The original connection will be disabled.

        Args:
            genotype (Genotype): The genotype to mutate.
        """

        length = len(genotype.connection_genes)
        index = random.randrange(0, length)
        originalConnection = genotype.connection_genes[index]
        originalConnection.enabled = False

        # TODO Rethink this now that 'order' has been removed
        newNode = NodeGene(NodeType.HIDDEN, bias=0)

        genotype.add_node(newNode)

    def add_connection_mutate(self, genotype: Genotype) -> None:
        """Given a genotype, add a connection between two randomly selected previously unconnected nodes.
        The new connection will have a weight of 1.

        Args:
            genotype (Genotype): The genotype to mutate.
        """

        # First we need to select a random node to attempt to mutate

        # Next, we need to try and pair it with another node it is not currently connected to in the same direction

        # If the second selected node is connected then select a new first node.

        indexes = list(range(len(genotype.node_genes)))
        random.shuffle(indexes)

        # Dictionaries guarantee preservation of insertion order.
        firstList = dict((i, None) for i in indexes)

        random.shuffle(indexes)
        secondList = dict((i, None) for i in indexes)

        found: "Optional[Tuple[int, int]]" = None

        for first in firstList.keys():
            connectionsFromFirst = set(
                conn.to for conn in genotype.connection_genes if conn.source == first)
            for second in secondList.keys():
                if not second in connectionsFromFirst:
                    found = (first, second)
                    break
            else:
                continue
            break

        # TODO
        # Unlikely, but we cannot do this mutation. How to handle? For now we can just do nothing
        # But we should probably mark this event somehow with a return value.
        if found == None:
            return

        # Now we have a pair of nodes that we can connect, we need to connect them.
        # However, it isn't as simple as that. What the hell do we do to calculate the order?
        # This is gonna get messy, so perhaps we should rethink our approach
