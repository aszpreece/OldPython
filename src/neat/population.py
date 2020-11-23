from typing import Optional


from src.neat.genotype import Genotype


class Population:
    def __init__(self) -> None:
        self.population = []
        self.total_fitness = 0
        self.total_adjusted_fitness = 0
        self.best_individual: Optional[Genotype] = None

    def add_member(self, genotype: Genotype):
        self.population.append(genotype)
