import logging
from src.neat.species import Species
from src.neat.neat_config import NeatConfig
from src.neat.genotype import Genotype
from typing import List, Tuple
from src.queue.reversible_queue import DualPriorityQueue


class ReproductionManager:
    def reproduce(self, population, species, neat_config: NeatConfig):
        pass


class DefaultReproductionManager(ReproductionManager):
    def reproduce(self, population, species, neat_config: NeatConfig):
        """Create a new generation from the fitness scores of the previous generation
        """
        # Figure out the babies each species deserve
        # (Total Adjusted Fitness in species) / (Average species fitness)
        babies_per_species = DualPriorityQueue(
            len(species), True)

        fitness_of_remaining_species = 0
        remaining_species = 0

        for species_id, s in species.items():

            total, maximum = s.get_total_and_max_fitness()

            if maximum > s.best_score:
                s.best_score = maximum
                s.cycles_since_improvement = 0
            else:
                s.cycles_since_improvement += 1

            if s.cycles_since_improvement < neat_config.species_stag_thresh:
                adjusted_fitness_of_species = total / s.count()
                fitness_of_remaining_species += adjusted_fitness_of_species
                remaining_species += 1
                babies_per_species.put(
                    adjusted_fitness_of_species, species_id)
            else:
                logging.debug(f'Species {species_id} has stagnated')

        babies_given_out = 0
        new_population: List[Genotype] = []

        if not remaining_species == 0:

            average_fitness_per_species = max(fitness_of_remaining_species /
                                              remaining_species, 0.001)

            # Copy across best individual unmodified
            assert population.best_individual is not None and population.best_individual.species is not None
            new_population.append(population.best_individual.copy())
            babies_given_out += 1

            while len(babies_per_species.queue) > 0:
                adjusted_fitness, species_id = babies_per_species.get()
                share = adjusted_fitness / average_fitness_per_species
                share = (share * neat_config.generation_size) / \
                    remaining_species

                babies_int = max(round(share), 1)

                logging.debug(
                    f'Babies for species {species_id}: {babies_int}: TAF: {adjusted_fitness}')

                # Adjust if we have gone over the limit
                if babies_given_out + babies_int > neat_config.generation_size:
                    babies_int = neat_config.generation_size - babies_given_out

                self.create_species_offspring(species[species_id],
                                              babies_int, neat_config, new_population)

                babies_given_out += babies_int

        # Just give any remaining babies to the best species
        if babies_given_out < neat_config.generation_size:
            babies_left = neat_config.generation_size - babies_given_out
            assert population.best_individual is not None and population.best_individual.species is not None
            self.create_species_offspring(
                population.best_individual.species, babies_left, neat_config, new_population)
            babies_given_out += babies_left
            print(f'babies left {babies_left}')

        population.population = new_population
        assert babies_given_out == neat_config.generation_size, 'Not given out enough babies'
        assert len(
            population.population) == neat_config.generation_size, 'New generation size is incorrect'

    def create_species_offspring(self, species: Species, babies_allocated: int, config: NeatConfig, new_population) -> None:

        average_fitness = species.get_total_and_max_fitness()[
            0] / species.count()

        fit_members_count = 0
        fittest_members: List[Genotype] = []

        # Sort members in descending order of fitness
        species.members.sort(
            key=lambda genotype: genotype.fitness, reverse=True)

        i = 0
        while i < species.count():
            member = species.members[i]
            if fit_members_count < 2 or member.fitness >= average_fitness:
                fittest_members.append(member)
                fit_members_count += 1
                i += 1
            else:
                break

        assert fit_members_count > 0, 'No fit members of species/ species is empty!'

        babies_made = 0
        # if babies_allocated > 6:
        #     babies_made += 1
        #     logging.debug(
        #         f'Copying across unmodified member of species {species.species_id}')
        #     new_population.append(fittest_members[0].copy())

        i = 0
        while babies_made < babies_allocated:
            i = i % len(fittest_members)
            baby = fittest_members[i].copy()
            # Decide whether to crossover or not
            if config.neat_random.random() < config.prob_crossover:
                father = baby
                mother = config.neat_random.choice(fittest_members).copy()
                baby = config.mutation_manager.crossover(
                    father, mother, config)

            config.mutation_manager.mutate(baby, config)
            new_population.append(baby)
            babies_made += 1
            i += 1

        assert babies_made == babies_allocated, 'Not made enough babies to fill the amount allocated!'
