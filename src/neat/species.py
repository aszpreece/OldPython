
import logging
import math
from random import Random
from src.neat.helper import compare_connection_genes
from src.neat.neat_config import NeatConfig
from typing import List, Optional
from src.neat.genotype import Genotype


class Species:

    def __init__(self, species_id: int, prototype: Genotype):
        self.members: List[Genotype] = []
        self.prototype: Optional[Genotype] = prototype
        self.species_id = species_id
        self.age: int = 0
        self.best_score: float = 0
        self.cycles_since_improvement = 0

    def count(self):
        """Get the amount of members a species has

        Returns:
            int: Amount of members that species has
        """
        return len(self.members)

    def get_species_fitness(self) -> float:

        species_fitness_sum = 0
        for species_member in self.members:
            species_fitness_sum += species_member.fitness
            if species_member.fitness > self.best_score:
                self.best_score = species_member.fitness
                self.cycles_since_improvement = 0

        if self.cycles_since_improvement > 20:
            species_fitness_sum *= math.exp(-self.cycles_since_improvement - 20)
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

    def create_species_offspring(self, babies_allocated: int, config: NeatConfig, new_population) -> None:

        average_fitness = self.get_species_fitness() / self.count()

        fit_members_count = 0
        fittest_members: List[Genotype] = []

        # Sort members in descending order of fitness
        self.members.sort(
            key=lambda genotype: genotype.fitness, reverse=True)

        i = 0
        while i < self.count():
            member = self.members[i]
            if fit_members_count < 2 or member.fitness >= average_fitness:
                fittest_members.append(member)
                fit_members_count += 1
                i += 1
            else:
                break

        assert fit_members_count > 0, 'No fit members of species/ species is empty!'

        babies_made = 0
        if babies_allocated > 6:
            babies_made += 1
            logging.debug(
                f'Copying across unmodified member of species {self.species_id}')
            new_population.append(fittest_members[0].copy())

        i = 0
        while babies_made < babies_allocated:
            i = i % len(fittest_members)
            baby = fittest_members[i].copy()
            config.mutation_manager.mutate(baby)
            new_population.append(baby)
            babies_made += 1
            i += 1

        assert babies_made == babies_allocated, 'Not made enough babies to fill the amount allocated!'
