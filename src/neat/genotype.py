from __future__ import annotations
from collections import deque

import copy
import math
from src.neat.node_type import NodeType
from typing import Deque, List, Optional, Set
from src.neat.phenotype import Phenotype
from random import Random


def relu(x: float) -> float:
    if x < 0:
        return 0
    else:
        return x


def sigmoid(x: float) -> float:
    if x < 0:
        return math.exp(x)/(1+math.exp(x))
    else:
        return 1/(1+math.exp(-x))


def mod_sigmoid(x: float) -> float:
    return 2/(1+math.exp(-x)) - 1


def identity(x: float): return x


def relu_sig(x: float):
    if x < 0:
        return 0
    else:
        return 2/(1+math.exp(-x)) - 1


def tanh(x: float):
    return math.tanh(x)


def binary(x: float):
    if x <= 0:
        return 0
    else:
        return 1


activation_funcs = {
    'sigmoid': sigmoid,
    'relu': relu,
    'mod_sigmoid': mod_sigmoid,
    'identity': identity,
    'binary': binary,
    'tanh': tanh,
    'relu_sig': relu_sig
}


class NodeGene:
    innov_id: int
    type: NodeType

    def __init__(self, innov_id: int, type: NodeType, activation_func=sigmoid) -> None:
        self.type = type
        self.innov_id = innov_id
        self.activation_func = activation_func


class ConnectionGene:
    source: int
    to: int
    weight: float
    innov_id: int
    enabled: bool
    recurrent: bool

    def __init__(self, innov_id: int, source: int, to: int, weight: float, enabled=True, recurrent=False) -> None:
        self.source = source
        self.to = to
        self.weight = weight
        self.innov_id = innov_id
        self.enabled = enabled
        self.recurrent = recurrent


class Genotype:

    connection_genes: "list[ConnectionGene]"
    node_genes: "list[NodeGene]"
    node_innov_start: int
    conn_innov_start: int

    # species: "optional[genotype]"
    fitness: float
    adjusted_fitness: float

    def __init__(self) -> None:
        self.connection_genes = []
        self.node_genes = []
        self.node_innov_start = 0
        self.conn_innov_start = 0
        self.fitness = 0
        self.adjusted_fitness = 0
        self.node_name_map = {}
        self.species = None

    def get_enabled_connections_count(self):
        def enabled_genes_filter(gene: ConnectionGene) -> bool:
            return gene.enabled

        return len(list(filter(enabled_genes_filter, self.connection_genes)))

    def get_complexity(self):
        return len(self.node_genes), len(self.connection_genes), self.get_enabled_connections_count()

    def copy(self) -> Genotype:
        species = self.species
        self.species = None
        self.phenotype = None
        node_name_map = self.node_name_map
        # self.node_name_map = None
        c = copy.deepcopy(self)
        self.species = species
        # self.node_name_map = node_name_map
        # c.node_name_map = node_name_map.copy()
        return c

    def creates_cycle(self, connection: ConnectionGene):

        if (connection.source == connection.to):
            return True

        visited_set: Set[int] = set()
        stack: Deque[int] = deque()

        stack.append(connection.source)

        target = connection.to

        connection_dict = {}
        for gene in self.connection_genes:
            if not gene.recurrent and gene.enabled:
                connection_dict.setdefault(gene.to, []).append(gene.source)

        # Figure out if there is a cycle by traversing the neuron connections
        # in reverse starting from the node this connection connects 'from' and attempt to find
        # a route back to it whilst avoiding previously introduced recurrent connections
        while (len(stack) != 0):
            node = stack.pop()
            visited_set.add(node)

            for source in connection_dict.get(node, []):
                # check if we have found the target
                if source == target:
                    return True
                # Avoid nodes we have already visited
                if source in visited_set:
                    continue

                stack.append(source)

        return False

    def add_input(self, name: str):
        self.node_innov_start += 1
        self.node_genes.append(NodeGene(self.node_innov_start, NodeType.INPUT))
        self.node_name_map[name] = self.node_innov_start

    def add_output(self, name: str, activation_func):
        self.node_innov_start += 1
        self.node_genes.append(NodeGene(
            self.node_innov_start, NodeType.OUTPUT, activation_func=activation_func))
        self.node_name_map[name] = self.node_innov_start

    def from_dict(self, node_dict):
        # atm: string -> int
        # this array maps to these inputs
        # how to mark string -> int as array?

        for input in node_dict['data']['inputs']:
            if input.get('type', None) == 'array':
                for i in range(input.get('size', 0)):
                    self.add_input(input['name'] + f'__{i}')
            else:
                self.add_input(input['name'])

        for output in node_dict['data']['outputs']:
            self.add_output(
                output['name'], activation_funcs[output['function']])


def generate_perceptron_connections(genotype: Genotype, random: Random, mu=0, sigma=1.5, chance_to_generate=1.0):
    """
        Generates connections from every input to every output with a randomized weight controlled by mu and sigma.
    """
    inputs = list(filter(lambda c: c.type ==
                         NodeType.INPUT, genotype.node_genes))
    outputs = list(filter(lambda c: c.type ==
                          NodeType.OUTPUT, genotype.node_genes))
    innov = 0
    for i in inputs:
        for o in outputs:
            if random.random() < chance_to_generate:
                genotype.connection_genes.append(ConnectionGene(
                    innov, i.innov_id, o.innov_id, random.normalvariate(0, sigma)))
                innov += 1
