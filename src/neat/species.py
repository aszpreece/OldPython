
import logging
import math
from random import Random
from src.neat.helper import compare_connection_genes
from src.neat.neat_config import NeatConfig
from typing import List, Optional, Tuple
from src.neat.genotype import Genotype


class Species:

    def __init__(self, species_id: int, prototype: Genotype):
        self.members: List[Genotype] = []
        self.prototype: Optional[Genotype] = prototype
        self.species_id = species_id
        self.age: int = 0
        self.cycles_since_improvement = 0

    def count(self):
        """Get the amount of members a species has

        Returns:
            int: Amount of members that species has
        """
        return len(self.members)

    def get_species_fitness(self) -> float:

        max_fitness = None
        species_fitness_sum = 0
        for species_member in self.members:
            species_fitness_sum += species_member.fitness

        return species_fitness_sum

    def cycle(self, rand: Random):

        self.age += 1
        self.prototype = rand.choice(self.members)
        self.members = []

    def add_member(self, genotype: Genotype):
        """Add a member to this species. Takes care of setting properties on the given genotype.

        Args:
            genotype (Genotype): Genotype to add to species.
        """
        genotype.species = self
        self.members.append(genotype)

    def similarity_operator(self, gen1: Genotype, config: NeatConfig) -> float:
        """Calculates if the given genome is compatible with this species

        Args:
            gen1 (Genotype): genotype.

        Returns:
            float: similarity score based on the hyper params:
                self.sim_disjoint_weight
                self.sim_excess_weight
                self.sim_weight_diff_weight
        """

        disjoint_conns, excess_conns, weight_diff_average = compare_connection_genes(
            gen1.connection_genes, self.prototype.connection_genes)

        # disjoint_nodes, excess_nodes = compare_node_genes(
        #     gen1.node_genes, gen2.node_genes)

        disjoints = disjoint_conns  # + disjoint_nodes
        excesses = excess_conns  # + excess_nodes

        normalisation_factor = max(
            len(gen1.connection_genes) + len(gen1.node_genes),
            len(self.prototype.connection_genes) + len(self.prototype.node_genes))
        if normalisation_factor > config.sim_genome_length_threshold:
            normalisation_factor = 1

        return (disjoints * config.sim_disjoint_weight) / normalisation_factor + \
            (excesses * config.sim_excess_weight) / normalisation_factor + \
            weight_diff_average * config.sim_weight_diff_weight
