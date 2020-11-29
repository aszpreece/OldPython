
from src.neat.neat import NEAT
from experiment.run_experiment import train_neat
from src.neat.mutate import DefaultMutationManager
from src.neat.reproduction import DefaultReproductionManager
from experiment.flappy_swarm.flappy_swarm import BirdBrain, FlappySwarm, visualize
from src.neat.node_type import NodeType
from src.neat.genotype import Genotype, NodeGene, mod_sigmoid, sigmoid
from src.neat.phenotype import Phenotype
from src.neat.neat_config import NeatConfig
import logging

bird_base = Genotype()

bird_base.node_genes = [
    NodeGene(0, NodeType.BIAS),  # Bias node
    NodeGene(1, NodeType.INPUT),  # Obstacle in front (1 if true 0 else)
    # Sound above (normalized for amount of birds)
    NodeGene(2, NodeType.INPUT),

    NodeGene(3, NodeType.INPUT),  # Sound below
    NodeGene(4, NodeType.INPUT),  # Distance to next obstacle
    # Movement of bird
    NodeGene(5, NodeType.OUTPUT, activation_func=mod_sigmoid),
    # Sound from bird
    NodeGene(6, NodeType.OUTPUT, activation_func=sigmoid),
    NodeGene(7, NodeType.INPUT),  # Dist below
    NodeGene(8, NodeType.INPUT),  # Dist above
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


class NeatBirdBrain(BirdBrain):

    def __init__(self, genotype: Genotype) -> None:
        self.phenotype = Phenotype(genotype)

    def get_movement(self) -> float:
        return self.phenotype.node_activations.get(5, 0)

    def get_sound(self) -> float:
        return self.phenotype.node_activations.get(6, 0)

    def update(self, above_sound, below_sound, obst_in_front, dist_below, dist_above, obst_dist=0) -> None:
        self.phenotype.calculate({
            0: 1,
            1: obst_in_front,
            2: above_sound,
            3: below_sound,
            4: obst_dist,
            7: dist_below,
            8: dist_above
        })


def bird_fitness(genotype: Genotype):
    # Create a bunch of bird brains and put them in a simulation

    n = 5
    score_total = 0
    for i in range(n):
        brains = [NeatBirdBrain(genotype) for i in range(6)]
        simulation = FlappySwarm(brains)

        while len(simulation.birds) > 3 and simulation.obstacles_cleared < 30:
            simulation.update()

        score_total += simulation.score

    return score_total / n


def result_func(neat: NEAT):
    if neat.population.best_individual is not None and neat.generation_num % 20 == 0:
        brains = [NeatBirdBrain(neat.population.best_individual)
                  for i in range(6)]
        simulation = FlappySwarm(brains)
        visualize(simulation)


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
    prob_to_connect_nodes=0.5,
    prob_to_split_connection=0.2
)

logging.basicConfig(level=logging.NOTSET)
train_neat(bird_fitness, config, 1320, result_func=result_func)
