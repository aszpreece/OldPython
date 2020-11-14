from enum import Enum


class NodeType(Enum):
    INPUT = 1
    HIDDEN = 2
    OUTPUT = 3


class NodeGene:
    innov_id: int
    type: NodeType
    bias: float

    def __init__(self, innov_id: int, type: NodeType, bias: float = 0.0) -> None:
        self.type = type
        self.bias = bias
        self.innov_id = innov_id


class ConnectionGene:
    source: int
    to: int
    weight: float
    innov_id: int

    def __init__(self, innov_id: int, source: int, to: int, weight: float) -> None:
        self.source = source
        self.to = to
        self.weight = weight
        self.innov_id = innov_id
        self.enabled = True


class Genotype:
    connection_genes: "list[ConnectionGene]"
    node_genes: "list[NodeGene]"

    def __init__(self) -> None:
        self.connection_genes = []
        self.node_genes = []
        self.next_node_id = 0
