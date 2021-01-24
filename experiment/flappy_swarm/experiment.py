
from operator import mod
from random import Random, normalvariate
from sys import platform
from src.neat.neat import NEAT
from experiment.run_experiment import train_neat
from src.neat.mutate import DefaultMutationManager
from src.neat.reproduction import DefaultReproductionManager
from experiment.flappy_swarm.flappy_swarm import BirdBrain, FlappySwarm, visualize, FlappySwarmConfig
from src.neat.node_type import NodeType
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, mod_sigmoid, sigmoid
from src.neat.phenotype import Phenotype
from src.neat.neat_config import NeatConfig
import numpy as np
import logging
import pickle
from datetime import datetime
from experiment.save_genome import save_genome
import random
import concurrent.futures


bird_base = Genotype()


def steep_sigmoid(x):
    return (1 / (1 + np.exp(-4.7 * x)) - 0.5) * 2


bird_base.node_genes = [
    NodeGene(0, NodeType.BIAS),  # Bias node
    NodeGene(1, NodeType.INPUT),  # Obstacle in front (1 if true 0 else)

    # # Sound above (normalized for amount of birds)
    NodeGene(2, NodeType.INPUT),
    NodeGene(3, NodeType.INPUT),  # Sound below

    # NodeGene(2, NodeType.INPUT),  # +1 for sound louder above, -1 if below

    NodeGene(4, NodeType.INPUT),  # Distance to next obstacle
    # Movement of bird
    NodeGene(5, NodeType.OUTPUT, activation_func=mod_sigmoid),
    # Sound from bird
    NodeGene(6, NodeType.OUTPUT, activation_func=sigmoid),
    # NodeGene(7, NodeType.INPUT),  # Dist below
    # NodeGene(8, NodeType.INPUT),  # Dist above
]

# Set up perceptron
bird_base.connection_genes = [
    # ConnectionGene(0, 1, 5, 0),
    # ConnectionGene(1, 2, 5, 0),
    # ConnectionGene(2, 3, 5, 0),
    # ConnectionGene(3, 4, 5, 0),
    # ConnectionGene(4, 5, 5, 0),

    # ConnectionGene(5, 1, 6, 0),
    # ConnectionGene(6, 2, 6, 0),
    # ConnectionGene(7, 3, 6, 0),
    # ConnectionGene(8, 4, 6, 0),
    # ConnectionGene(9, 5, 6, 0),

    # ConnectionGene(10, 7, 5, 0),
    # ConnectionGene(11, 8, 6, 0),
]

bird_base.conn_innov_start = 11
bird_base.node_innov_start = 8

input_noise = Random()


class NeatBirdBrain(BirdBrain):

    def __init__(self, genotype: Genotype) -> None:
        self.phenotype = Phenotype(genotype)

    def get_movement(self) -> float:
        return self.phenotype.node_activations.get(5, 0)

    def get_sound(self) -> float:
        return self.phenotype.node_activations.get(6, 0)

    def update(self, above_sound, below_sound, obst_in_front, dist_below, dist_above, obst_dist=0) -> None:

        # below_above = 0
        # if above_sound > below_sound:
        #     below_above = 1
        # elif below_sound > above_sound:
        #     below_above = -1

        self.phenotype.calculate({
            0: 1,
            1: obst_in_front,
            # 2: below_above,
            2: above_sound,
            3: below_sound,
            4: obst_dist,
            # 7: dist_below,
            # 8: dist_above
        })


num_birds = 12




def result_func(neat: NEAT):


    if neat.population.best_individual is not None:
        save_genome(neat.population.best_individual, neat.run_id, 'flappy', neat.generation_num)


def thread_experiment( noise, run_num):

    print(f'Running noise {noise} run num {run_num}')
    
    def bird_fitness(genotype: Genotype):
        # Create a bunch of bird brains and put them in a simulation

        n = 5
        score_total = 0
        for i in range(n):
            brains = [NeatBirdBrain(genotype) for i in range(num_birds)]
            simulation = FlappySwarm(brains, FlappySwarmConfig(detector_noise_std=noise, communication=True))

            while len(simulation.birds) and simulation.obstacles_cleared < 10:
                simulation.update()

            if simulation.bird_edge_crashes == 0:
                score_total += simulation.score

        return score_total / n
    config = NeatConfig(
        activation_func=sigmoid,
        fitness_function=bird_fitness,
        base_genotype=bird_base,
        reproduction=DefaultReproductionManager(),
        generation_size=150,
        mutation_manager=DefaultMutationManager(12, 9),
        species_target=10,
        species_mod=0.1,
        prob_crossover=0.8,
        weight_perturb_scale=1,
        new_weight_power=0.8,
        sim_disjoint_weight=1.0,
        sim_excess_weight=1.0,
        sim_weight_diff_weight=0.3,
        sim_genome_length_threshold=20,
        sim_threshold=3.0,
        species_stag_thresh=40,
        allow_recurrence=False,
        prob_inherit_from_fitter=0.5,
        weight_random_type='gaussian',
        run_id=f'[{noise}][{run_num}]'
    )

    logging.basicConfig(level=logging.WARNING)
    data = train_neat(fitness_func=bird_fitness, config=config,target_score=None,result_func=result_func, generations=120)
    with open(f'./results/{config.run_id}', 'wb') as f:
        pickle.dump(data, f)
    
if __name__ == "__main__":

    #TODO one extra 0.0 needed
    noise_vals = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8]
    runs_per_val = 14

    def error(err):
        print(err)

    import multiprocessing as mp
    pool = mp.Pool(mp.cpu_count())
    args = [(n, r) for r in range(runs_per_val) for n in noise_vals]
    results = [pool.apply_async(thread_experiment, a, error_callback=error) for a in args]
    pool.close()
    pool.join()


    