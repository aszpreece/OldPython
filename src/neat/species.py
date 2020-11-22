
import math
from random import Random
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
