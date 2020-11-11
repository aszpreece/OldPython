from enum import Enum


class NodeType(Enum):
    INPUT = 1
    HIDDEN = 2
    OUTPUT = 3


class NodeGene:
    id: int
    type: NodeType
    order: float
    bias: float

    def __init__(self, type: NodeType, order: float, bias: float = 0.0, id: int = -1):
        self.id = id
        self.type = type
        self.bias = bias
        # This order value helps us to figure out the order in which this node must be evaluated
        # Values with a lower order must be evaluated before any nodes with a higher order.
        # If a nodes relies on a node with a higher order than itself then that connection must
        # be marked as recurrent. This means it must treat the node as if it had the output value from
        # The previous execution
        self.order = order


class ConnectionGene:
    source: int
    to: int
    weight: float
    in_id: int
    recurrent: bool

    def __init__(self, source: int, to: int, weight: float, in_id: int, recurrent: bool = False):
        self.source = source
        self.to = to
        self.weight = weight
        self.in_id = in_id
        self.enabled = True
        self.recurrent = recurrent


class Genotype:
    connection_genes: "list[ConnectionGene]"
    node_genes: "list[NodeGene]"
    next_node_id: int

    def __init__(self):
        self.connection_genes = []
        self.node_genes = []
        self.next_node_id = 0

    def add_node(self, node_gene: NodeGene) -> None:
        """Add a node to the genotype.
        The added node will have its id property set

        Args:
            node_gene (NodeGene): The node to add
        """
        node_gene.id = self.node_id
        self.node_id += 1
