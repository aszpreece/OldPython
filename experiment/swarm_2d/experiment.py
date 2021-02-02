
from operator import mod
from random import Random, normalvariate
from sys import platform
from src.neat.neat import NEAT
from experiment.run_experiment import train_neat
from src.neat.mutate import DefaultMutationManager
from src.neat.reproduction import DefaultReproductionManager
from experiment.swarm_2d.swarm_2d import CreatureBrain2D, Swarm2D, visualize, Swarm2DConfig
from src.neat.node_type import NodeType
from src.neat.genotype import ConnectionGene, Genotype, NodeGene, mod_sigmoid, sigmoid, generate_perceptron_connections
from src.neat.phenotype import Phenotype
from src.neat.neat_config import NeatConfig
import numpy as np
import logging
import pickle
from datetime import datetime
from experiment.save_genome import save_genome
import random


creature_base = Genotype()


def steep_sigmoid(x):
    return (1 / (1 + np.exp(-4.7 * x)) - 0.5) * 2


creature_base.node_genes = [
    NodeGene(0, NodeType.BIAS),  # Bias node
    NodeGene(1, NodeType.INPUT),  # Obstacle in front (1 if true 0 else)

    # Sound for each ear (normalized for amount of birds)
    NodeGene(2, NodeType.INPUT),
    NodeGene(3, NodeType.INPUT),
    NodeGene(4, NodeType.INPUT),
    NodeGene(5, NodeType.INPUT),
    NodeGene(6, NodeType.INPUT),
    NodeGene(7, NodeType.INPUT),
    NodeGene(8, NodeType.INPUT),
    NodeGene(9, NodeType.INPUT),

    # X and Y normalized
    NodeGene(10, NodeType.INPUT),
    NodeGene(11, NodeType.INPUT),


    NodeGene(12, NodeType.INPUT),  # Distance to next obstacle
    # Movement of bird
    NodeGene(13, NodeType.OUTPUT, activation_func=steep_sigmoid),
    # Rotation of bird
    NodeGene(14, NodeType.OUTPUT, activation_func=steep_sigmoid),
    # Sound from bird
    NodeGene(15, NodeType.OUTPUT, activation_func=sigmoid),
]

# creature_base.conn_innov_start = 11
# creature_base.node_innov_start = 16

input_noise = Random()
random_weights = Random()

generate_perceptron_connections(creature_base, random_weights)

class NeatBrain2D(CreatureBrain2D):

    def __init__(self, genotype: Genotype) -> None:
        self.phenotype = Phenotype(genotype)

    def get_movement(self) -> float:
        return self.phenotype.node_activations.get(13, 0)

    def get_rotation(self) -> float:
        return self.phenotype.node_activations.get(14, 0)

    def get_sound(self) -> float:
        return self.phenotype.node_activations.get(15, 0)

    def update(self, sounds, obst_in_front, x, y, obst_dist=0) -> None:
        input_dict = {
            0: 1,
            1: obst_in_front,
            10: x,
            11: y,
            12: obst_dist,
        }

        for i, sound in enumerate(sounds):
            input_dict[i + 2] = sound

        self.phenotype.calculate(input_dict)


num_birds = 12


def result_func(neat: NEAT):

    if neat.population.best_individual is not None:
        save_genome(neat.population.best_individual,
                    neat.run_id, 'swarm2d', neat.generation_num)


def thread_experiment(noise, run_num):

    print(f'Running noise {noise} run num {run_num}')

    def bird_fitness(genotype: Genotype):
        # Create a bunch of bird brains and put them in a simulation

        n = 5
        score_total = 0

        for i in range(n):
            brains = [NeatBrain2D(genotype) for i in range(num_birds)]
            simulation = Swarm2D(brains, Swarm2DConfig(
                detector_noise_std=noise, communication=True))

     
            while len(simulation.birds) and simulation.obstacles_cleared < 10:
                simulation.update()

            if simulation.bird_edge_crashes == 0:
                score_total += simulation.score

        return score_total / n

    config = NeatConfig(
        activation_func=sigmoid,
        fitness_function=bird_fitness,
        base_genotype=creature_base,
        reproduction=DefaultReproductionManager(),
        generation_size=150,
        mutation_manager=DefaultMutationManager(creature_base),
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
    data = train_neat(fitness_func=bird_fitness, config=config,
                      target_score=None, result_func=result_func, generations=120)
    with open(f'./results/{config.run_id}', 'wb') as f:
        pickle.dump(data, f)


if __name__ == "__main__":

    # TODO one extra 0.0 needed
    noise_vals = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8]
    runs_per_val = 14

    def error(err):
        print(err)

    import multiprocessing as mp
    pool = mp.Pool(mp.cpu_count())
    args = [(n, r) for r in range(runs_per_val) for n in noise_vals]
    results = [pool.apply_async(
        thread_experiment, a, error_callback=error) for a in args]
    pool.close()
    pool.join()
