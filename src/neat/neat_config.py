from random import Random
from typing import Literal, Union
from src.neat.genotype import sigmoid


class NeatConfig():

    def __init__(self,
                 activation_func,
                 fitness_function,
                 base_genotype,
                 mutation_manager,
                 reproduction,
                 weight_perturb_scale=1,
                 prob_perturbing_weight=0.8,
                 prob_reset_weight=0.1,
                 prob_enable_conn=0.01,
                 prob_disable_conn=0.01,
                 new_weight_power=4,
                 prob_to_split_connection=0.03,
                 prob_to_connect_nodes=0.05,
                 generation_size=150,
                 sim_disjoint_weight=1.0,
                 sim_excess_weight=1.0,
                 sim_weight_diff_weight=0.5,
                 sim_genome_length_threshold=20,
                 sim_threshold=3.0,
                 species_target=None,
                 species_mod=0.3,
                 species_stag_thresh=40,
                 neat_random=Random(),
                 allow_recurrence=False,
                 prob_inherit_from_fitter=0.5,
                 prob_crossover=0.0,
                 weight_random_type='gaussian',
                 run_id='',
                 fitness_function_type: Union[Literal['population'], Literal['individual']] ='individual', # individual or population
                 initial_seeding_style: Union[Literal['homogenous'], Literal['random']] = 'homogenous', # homogenous means the initial population are all the same. if they are random, then each one is set to be a randomly generated perceptron
                 ):

        self.reproduction = reproduction
        self.mutation_manager = mutation_manager
        self.base_genotype = base_genotype
        self.neat_random = neat_random

        # Hyperparams for weight mutation
        self.weight_perturb_scale = weight_perturb_scale
        self.prob_perturbing_weight = prob_perturbing_weight
        self.prob_reset_weight = prob_reset_weight
        self.prob_enable_conn = prob_enable_conn
        self.prob_disable_conn = prob_disable_conn

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
        self.species_stag_thresh = species_stag_thresh

        self.allow_recurrence = allow_recurrence

        # Probability of inheriting a matching gene from the fitter parent vs the less fitter
        self.prob_inherit_from_fitter = prob_inherit_from_fitter
        self.prob_crossover = prob_crossover

        self.activation_func = activation_func

        self.weight_random_type = weight_random_type
        self.run_id = run_id
        self.fitness_function_type = fitness_function_type
        self.initial_seeding_style = initial_seeding_style

    def get_weight_delta(self) -> float:
        if self.weight_random_type == 'uniform':
            return self.neat_random.uniform(-1, 1)
        elif self.weight_random_type == 'gaussian':
            return self.neat_random.gauss(0, 0.4)
        else:
            raise Exception('Invalid weight_random_type')
