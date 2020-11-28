import random
from src.neat.population import Population
from src.neat.neat_config import NeatConfig
from src.neat.species import Species
from src.neat.helper import compare_connection_genes, compare_node_genes
from typing import Callable, Dict, List, Optional, Tuple
from random import Random
from queue import PriorityQueue
import logging
import copy
import math


from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType


class NEAT:

    def __init__(self, neat_config: NeatConfig) -> None:

        self.config = neat_config
        self.population = Population()
        self.species: Dict[int, Species] = {}
        self.species_index = 0
        self.generation_num = 0

    def get_next_species_number(self):
        self.species_index += 1
        return self.species_index

    def run_generation(self) -> Genotype:
        """Runs a generation and returns the genotype of the highest performer.

        Returns:
            Genotype: The genotype of the best performing member.
        """

        self.generation_num += 1
        if self.generation_num != 1:
            self.config.mutation_manager.cycle()
            self.config.reproduction.reproduce(
                self.population, self.species, self.config)
        else:
            for i in range(self.config.generation_size):
                genotype_copy = copy.deepcopy(self.config.base_genotype)
                self.population.add_member(genotype_copy)

        self.adjust_compatibility()
        self.cycle_species()
        self.place_into_species()

        self.population.best_individual = None

        self.population.total_fitness = 0
        self.population.total_adjusted_fitness = 0
        for genotype in self.population.population:

            score = self.config.fitness_function(genotype)
            genotype.fitness = score
            genotype.adjusted_fitness = score / genotype.species.count()
            self.population.total_fitness += genotype.fitness
            self.population.total_adjusted_fitness += genotype.adjusted_fitness

            if self.population.best_individual == None or genotype.fitness > self.population.best_individual.fitness:
                self.population.best_individual = genotype

        assert self.population.best_individual is not None
        return self.population.best_individual

    def adjust_compatibility(self):
        if self.config.species_target is not None:
            if len(self.species) > self.config.species_target:
                self.config.sim_threshold += self.config.species_mod
            elif len(self.species) < self.config.species_target:
                self.config.sim_threshold -= self.config.species_mod

    def cycle_species(self):
        """Select a random member of each species to be the species representative for the next generation and reset their memberships
        """
        for species_id, species in self.species.items():
            species.cycle(self.config.neat_random)

    def place_into_species(self) -> None:
        """Place the the population into species or create a new one if not compatible

        Args:
            genotype (Genotype): Genotype to place into species
        """
        #
        for genotype in self.population.population:
            for species_id, species in self.species.items():
                assert species.prototype is not None
                if species.similarity_operator(genotype, self.config) <= self.config.sim_threshold:
                    species.add_member(genotype)
                    break
            else:
                # Create new species if none match
                new_species_num = self.get_next_species_number()
                new_species = Species(new_species_num, genotype)
                new_species.add_member(genotype)
                assert self.species.get(new_species_num) is None
                self.species[new_species_num] = new_species

                logging.info(f'Creating new species {new_species_num}')

        extinct: List[int] = []
        for species_id, species in self.species.items():
            if len(species.members) == 0:
                logging.info(
                    f'Species {species.species_id} has died out at age {species.age}')
                extinct.append(species.species_id)

        for species_id in extinct:
            del self.species[species_id]

    def print_species(self):
        if len(self.species) == 0:
            logging.debug(f'NO SPECIES')
        for species_id, species in self.species.items():
            logging.debug(
                f'SPECIES {species_id} SIZE: {species.count()} AGE: {species.age} STAGNANT: {species.cycles_since_improvement}')
