from src.neat.population import Population
from src.neat.neat_config import NeatConfig
from src.neat.genotype import Genotype
from typing import List, Tuple
import PriorityQueue


class ReproductionManager:
    def reproduce(self, population, species, config: NeatConfig):
        pass


class DefaultReproductionManager(ReproductionManager):
    def reproduce(self, population, species, config: NeatConfig):
        """Create a new generation from the fitness scores of the previous generation
        """
        # Figure out the babies each species deserve
        # (Total Adjusted Fitness in species) / (Average species fitness)
        babies_per_species: PriorityQueue[Tuple[float, int]] = PriorityQueue(
            len(species))

        average_fitness_per_species = population.total_adjusted_fitness / \
            len(species)

        for species_id, species in species.items():
            adjusted_fitness_of_species = species.get_species_fitness() / species.count()

            share = adjusted_fitness_of_species / average_fitness_per_species

            share = (share * config.generation_size) / len(species)

            babies_per_species.put((share, species_id))

        babies_given_out = 0

        new_population: List[Genotype] = []
        # Copy across best individual unmodified
        assert population.best_individual is not None and population.best_individual.species is not None
        new_population.append(population.highest_performer.copy())
        babies_given_out += 1

        while len(babies_per_species.queue) > 0:
            babies_float, species_id = babies_per_species.get()
            babies_int = max(round(babies_float), 1)

            # Adjust if we have gone over the limit
            if babies_given_out + babies_int > config.generation_size:
                babies_int = config.generation_size - babies_given_out

            species[species_id].create_species_offspring(
                babies_int, config, new_population)

            babies_given_out += babies_int

        # Just give any remaining babies to the best species
        if babies_given_out < config.generation_size:
            babies_left = config.generation_size - babies_given_out
            assert population.best_individual is not None and population.best_individual.species is not None
            population.best_individual.species.create_species_offspring(
                babies_left, new_population)
            babies_given_out += babies_left

        population.population = new_population
        assert babies_given_out == config.generation_size, 'Not given out enough babies'
        assert len(
            population.population) == config.generation_size, 'New generation size is incorrect'
