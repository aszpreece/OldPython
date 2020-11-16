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
    enabled: bool

    def __init__(self, innov_id: int, source: int, to: int, weight: float, enabled=True) -> None:
        self.source = source
        self.to = to
        self.weight = weight
        self.innov_id = innov_id
        self.enabled = enabled


class Genotype:
    connection_genes: "list[ConnectionGene]"
    node_genes: "list[NodeGene]"
    node_innov_start: int
    conn_innov_start: int

    def __init__(self) -> None:
        self.connection_genes = []
        self.node_genes = []
        self.node_innov_start = 0
        self.conn_innov_start = 0

    def get_enabled_connections_count(self):
        def enabled_genes_filter(gene: ConnectionGene) -> bool:
            return gene.enabled

        return len(list(filter(enabled_genes_filter, self.connection_genes)))

    def get_complexity(self):
        return (len(self.node_genes), len(self.connection_genes), self.get_enabled_connections_count())
