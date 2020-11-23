from random import Random
from src.neat.reproduction import DefaultReproductionManager
from src.neat.mutate import DefaultMutationManager


class NeatConfig():

    def __init__(self,
                 fitness_function,
                 base_genotype,
                 mutation_manager=DefaultMutationManager(),
                 reproduction=DefaultReproductionManager(),
                 prob_to_mutate_weights=0.8,
                 weight_perturb_scale=0.45,
                 prob_perturbing_weights=0.95,
                 new_weight_power=1.2,
                 prob_to_split_connection=0.03,
                 prob_to_connect_nodes=0.05,
                 generation_size=150,
                 sim_disjoint_weight=1.0,
                 sim_excess_weight=1.0,
                 sim_weight_diff_weight=0.4,
                 sim_genome_length_threshold=20,
                 sim_threshold=3.0,
                 species_target=None,
                 species_mod=0.3,
                 neat_random=Random()
                 ):

        self.reproduction = reproduction
        self.mutation_manager = mutation_manager
        self.base_genotype = base_genotype
        self.neat_random = neat_random

        # Hyperparams for weight mutation
        self.prob_to_mutate_weights = prob_to_mutate_weights
        self.weight_perturb_scale = weight_perturb_scale
        self.prob_perturbing_weights = prob_perturbing_weights
        self.new_weight_power = new_weight_power

        # Hyperparams for split connection mutation
        self.prob_to_split_connection = prob_to_split_connection

        # Hyperparams for new connection mutation
        self.prob_to_connect_nodes = prob_to_connect_nodes

        self.generation_size = generation_size
        self.fitness_function = fitness_function

        self.sim_disjoint_weight = sim_disjoint_weight
        self.sim_excess_weight = sim_excess_weight
        self.sim_weight_diff_weight = sim_weight_diff_weight
        self.sim_genome_length_threshold = sim_genome_length_threshold
        self.sim_threshold = sim_threshold

        self.species_target = species_target
        self.species_mod = species_mod
