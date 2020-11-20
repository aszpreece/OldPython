from __future__ import annotations

import copy

from src.neat.node_type import NodeType
from src.neat.species import Species
from typing import List, Optional
from src.neat.phenotype import Phenotype


calls = 0


class NodeGene:
    innov_id: int
    type: NodeType

    def __init__(self, innov_id: int, type: NodeType) -> None:
        self.type = type
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

    species: Optional[Species]
    fitness: float
    adjusted_fitness: float
    phenotype: Optional[Phenotype]

    def __init__(self) -> None:
        self.connection_genes = []
        self.node_genes = []
        self.node_innov_start = 0
        self.conn_innov_start = 0
        self.fitness = 0
        self.adjusted_fitness = 0
        self.species = None
        self.phenotype = None

    def get_enabled_connections_count(self):
        def enabled_genes_filter(gene: ConnectionGene) -> bool:
            return gene.enabled

        return len(list(filter(enabled_genes_filter, self.connection_genes)))

    def get_complexity(self):
        return len(self.node_genes), len(self.connection_genes), self.get_enabled_connections_count()

    def copy(self) -> Genotype:
        phenotype = self.phenotype
        self.phenotype = None
        c = copy.deepcopy(self)
        c.phenotype = phenotype
        self.phenotype = phenotype
        return c
