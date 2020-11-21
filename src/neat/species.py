
from random import Random
from typing import List, Optional
from src.neat.genotype import Genotype


class Species:

    def __init__(self, species_id: int, prototype: Genotype):
        self.members: List[Genotype] = []
        self.prototype: Optional[Genotype] = prototype
        self.species_id = species_id

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

        return species_fitness_sum

    def cycle(self, rand: Random):
        self.prototype = rand.choice(self.members)
        self.members = []

    def add_member(self, genotype: Genotype):
        """Add a member to this species. Takes care of setting properties on the given genotype.

        Args:
            genotype (Genotype): Genotype to add to species.
        """
        genotype.species = self
        self.members.append(genotype)
