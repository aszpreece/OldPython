import random
from src.neat.species import Species
from src.neat.helper import compare_connection_genes, compare_node_genes
from typing import Callable, Dict, List, Optional, Tuple
from random import Random
from queue import PriorityQueue
import logging
import copy
import math


from src.neat.genotype import ConnectionGene, Genotype, NodeGene, NodeType


class NEAT:

    neat_random: Random

    node_innovation_number: int
    connection_innovation_number: int

    prob_to_mutate_weights: float
    weight_perturb_scale: float
    prob_perturbing_weights: float
    new_weight_variance: float

    prob_to_split_connection: float

    prob_to_connect_nodes: float

    # CONNECTION_INNOV_ID -> (NEW_NODE_INNOV_ID, FROM_INNOV_ID, TO_INNOV_ID)
    split_signatures: Dict[int, Tuple[int, int, int]]
    # (FROM_NODE, TO_NODE) -> INNOV_ID
    new_conn_signatures: Dict[Tuple[int, int], int]

    population: List[Genotype]
    fitness_function: Callable[[Genotype], float]

    generation_size: int

    sim_disjoint_weight: float
    sim_excess_weight: float
    sim_weight_diff_weight: float
    sim_genome_length_threshold: int

    def __init__(self, base_genotype: Genotype, generation_size: int,  fitness_function: Callable[[Genotype], float],
                 neat_random=Random()) -> None:

        self.neat_random = neat_random

        # Set our initial innovation numbers so we don't overlap with the genes already in the base genotype
        self.node_innovation_number = base_genotype.node_innov_start
        self.connection_innovation_number = base_genotype.conn_innov_start

        # Hyperparams for best performing members
        self.percentage_top_networks_passed_on = 0.05

        # Hyperparams for weight mutation
        self.prob_to_mutate_weights = 0.8
        self.weight_perturb_scale = 1.0
        self.prob_perturbing_weights = 0.1
        self.new_weight_variance = 1.5

        # Hyperparams for split connection mutation
        self.prob_to_split_connection = 0.03

        # Hyperparams for new connection mutation
        self.prob_to_connect_nodes = 0.05

        self.split_signatures = {}
        self.new_conn_signatures = {}

        self.generation_size = generation_size
        # Create initial population

        self.fitness_function = fitness_function

        self.sim_disjoint_weight: float = 1.0
        self.sim_excess_weight: float = 1.0
        self.sim_weight_diff_weight: float = 0.4
        self.sim_genome_length_threshold: int = 20
        self.sim_threshold: float = 3.0

        self.species_index: int = 0
        self.population = []
        self.highest_performer: Optional[Genotype] = None

        self.species: Dict[int, Species] = {}

        for i in range(generation_size):
            genotype_copy = copy.deepcopy(base_genotype)
            self.population.append(genotype_copy)

    def get_next_node_innov_num(self):
        self.node_innovation_number += 1
        return self.node_innovation_number

    def get_next_conn_innov_num(self):
        self.connection_innovation_number += 1
        return self.connection_innovation_number

    def get_next_species_number(self):
        self.species_index += 1
        return self.species_index

    def create_species_offspring(self, species: Species, babies_allocated: int, new_population: List[Genotype]):

        average_fitness = species.get_species_fitness() / species.count()

        fit_members_count = 0
        fittest_members: List[Genotype] = []

        i = 0
        while i < species.count():
            member = species.members[i]
            if fit_members_count < 2 or member.fitness < average_fitness:
                fittest_members.append(member)
                fit_members_count += 1
            else:
                break
        else:
            assert False, 'No fit members of species/ species is empty!'

        # Sort members in descending order of fitness
        fittest_members.sort(
            key=lambda genotype: genotype.fitness, reverse=True)
        babies_made = 0
        if babies_allocated > 3:
            babies_made += 1
            logging.debug(
                f'Copying across unmodified member of species {species.species_id}')
            new_population.append(fittest_members[0].copy())

        i = 0
        while babies_made < babies_allocated:
            i = i % len(fittest_members)
            baby = fittest_members[i].copy()
            self.mutate(baby)
            new_population.append(baby)
            babies_made += 1

        assert babies_made == babies_allocated, 'Not made enough babies to fill the amount allocated!'

    def mutate(self, genotype: Genotype):
        """Mutate the given genotype
        """
        if self.neat_random.uniform(0, 1) <= self.prob_to_mutate_weights:
            self.weight_mutate(genotype, self.neat_random)
        if self.neat_random.uniform(0, 1) <= self.prob_to_split_connection:
            self.split_connection_mutate(genotype, self.neat_random)
        if self.neat_random.uniform(0, 1) <= self.prob_to_connect_nodes:
            self.add_connection_mutate(genotype, self.neat_random)

    def create_new_generation(self):
        """Create a new generation from the fitness scores of the previous generation
        """

        # Figure out the babies each species deserve
        # (Total Adjusted Fitness in species) / (Average species fitness)
        babies_per_species: PriorityQueue[Tuple[float, int]] = PriorityQueue(
            len(self.species))

        average_fitness_per_species = self.total_adjusted_fitness / \
            len(self.species)
        for species_id, species in self.species.items():
            adjusted_fitness_of_species = species.get_species_fitness() / species.count()

            share = adjusted_fitness_of_species / average_fitness_per_species

            share = (share * self.generation_size) / len(self.species)

            babies_per_species.put((share, species_id))

        babies_given_out = 0
        new_population: List[Genotype] = []
        while len(babies_per_species.queue) > 0:
            babies_float, species_id = babies_per_species.get()
            babies_int = max(round(babies_float), 1)

            # Adjust if we have gone over the limit
            if babies_given_out + babies_int > self.generation_size:
                babies_int = self.generation_size - babies_given_out

            self.create_species_offspring(
                self.species[species_id], babies_int, new_population)
            babies_given_out += babies_int

        # Just give any remaining babies to the best species
        if babies_given_out < self.generation_size:
            babies_left = self.generation_size - babies_given_out
            assert self.highest_performer is not None and self.highest_performer.species is not None
            self.create_species_offspring(
                self.highest_performer.species, babies_left, new_population)
            babies_given_out += babies_left

        assert babies_given_out == self.generation_size, 'Not given out enough babies'
        assert len(
            self.population) == self.generation_size, 'New generation size is incorrect'

    def run_generation(self) -> Genotype:
        """Runs a generation and returns the genotype of the highest performer.

        Returns:
            Genotype: The genotype of the best performing member.
        """
        self.cycle_species()
        self.create_new_generation()

        self.highest_performer: Optional[Genotype] = None

        self.total_fitness = 0
        self.total_adjusted_fitness = 0
        for genotype in self.population:

            score = self.fitness_function(genotype)
            genotype.fitness = score
            genotype.adjusted_fitness = score / genotype.species.count()
            self.total_fitness += genotype.fitness
            self.total_adjusted_fitness += genotype.adjusted_fitness

            if self.highest_performer == None or genotype.fitness > self.highest_performer.fitness:
                self.highest_performer = genotype

        assert self.highest_performer is not None
        return self.highest_performer

    def weight_mutate(self, genotype: Genotype, random: Random) -> None:
        """Given a genotype, mutate each weight.
        Weights have a chance of (1-self.chance_to_assign_random_weight) to have their weights perturbed by a scale of self.weight_perturb_scale.
        Weights have a chance of self.weight_perturb_scale to have their weight set to a random value.

        Args:
            genotype (Genotype): The genotype to mutate.
            random (Random): Instance of random to use.
        """

        for connection_gene in genotype.connection_genes:

            if random.uniform(0, 1) < self.prob_perturbing_weights:
                # Perturb the weights
                connection_gene.weight += random.uniform(-1, 1) * \
                    self.weight_perturb_scale
            else:
                connection_gene.weight = random.uniform(-4, 4)

    def split_connection_mutate(self, genotype: Genotype, random: Random) -> None:
        """Given a genotype, split a random connection and add an intermediate node.

        The weight of the connection between the original source node and the new will be the same as the connection we are splitting.
        The connection from the new node to the original from node will have the value 1.
        The original connection will be disabled.

        Args:
            genotype (Genotype): The genotype to mutate.
            random (Random): Instance of random to use.
        """

        # Decide on the connection to split

        # Fix: no longer tries to split disabled genes
        enabledGenes = list(filter(lambda conn: conn.enabled,
                                   genotype.connection_genes))
        length = len(enabledGenes)

        index = random.randrange(0, length)

        # Disable the current connection
        originalConnection = enabledGenes[index]
        originalConnection.enabled = False

        # See if this mutation has arisen in this generation and if so use the innovation ids from that mutation
        innovation_ids_tuple = self.split_signatures.get(
            originalConnection.innov_id)

        node_innov_id = None
        from_innov_id = None
        to_innov_id = None

        if not innovation_ids_tuple == None:
            node_innov_id, from_innov_id, to_innov_id = innovation_ids_tuple
            logging.debug(
                'Split node has happened before this generation. Using old innovation numbers.')

        else:
            node_innov_id = self.get_next_node_innov_num()
            from_innov_id = self.get_next_conn_innov_num()
            to_innov_id = self.get_next_conn_innov_num()
            # Post the created innovation numbers as a tuple
            self.split_signatures[originalConnection.innov_id] = (
                node_innov_id, from_innov_id, to_innov_id)

        # Create a new node with a the innovation number
        genotype.node_genes.append(NodeGene(node_innov_id,
                                            NodeType.HIDDEN))

        # New connection from old source to new node with weight of 1.0 to reduce impact
        genotype.connection_genes.append(ConnectionGene(
            from_innov_id, originalConnection.source, node_innov_id, 1.0))

        # New connection from new node to old to. Weight is that of the old connection
        genotype.connection_genes.append(ConnectionGene(
            to_innov_id, node_innov_id, originalConnection.to, originalConnection.weight))

    def add_connection_mutate(self, genotype: Genotype, random: Random) -> None:
        """Given a genotype, add a connection between two randomly selected previously unconnected nodes.
        The new connection will have a weight of 1.

        Args:
            genotype (Genotype): The genotype to mutate.
            random (Random): Instance of random to use.
        """

        # Shuffle two copies of the list of nodes. We can run through the first and attempt to pair it with a node from the second

        indexes = list(range(len(genotype.node_genes)))
        random.shuffle(indexes)

        # Dictionaries guarantee preservation of insertion order.
        firstList = dict(
            (genotype.node_genes[i].innov_id, None) for i in indexes)

        random.shuffle(indexes)

        # We cannot connect 'to' input or bias nodes so we should ignore them
        secondList = dict(
            (genotype.node_genes[i].innov_id, None) for i in indexes if genotype.node_genes[i].type != NodeType.INPUT and genotype.node_genes[i].type != NodeType.BIAS)

        # The pair we have found
        pair: "Optional[Tuple[int, int]]" = None

        re_enabled_flag = False

        for first in firstList.keys():

            # We need to find all the connections that originate at the first node we have selected and log their 'to' node
            conns_from_first: Dict[int, ConnectionGene] = dict(
                (conn.to, conn) for conn in genotype.connection_genes if conn.source == first)
            for second in secondList.keys():
                # Looping through the second list, check whether or not the second node is already connected to the first node (in the same direction)
                connection = conns_from_first.get(second, None)
                # If there is no connection gene at all there won't be an entry in the hash table and it will rteurn Nome
                if connection == None:
                    pair = (first, second)
                    break
                # If there is a disabled connection we should re enable it TODO is this okay?
                elif connection.enabled == False:
                    # Flag that we have re enabled a gene
                    re_enabled_flag = True
                    connection.enabled = True
                    break

            else:
                # If this node is connected to everything then we cannot connect it to a new node and we must select a new 'first node
                continue
            break

        if pair == None:
            # If we didn't
            if re_enabled_flag == False:
                # TODO
                # Unlikely (Famous last words), but we cannot do this mutation. We should log it
                logging.warn(
                    'Failed to create a new connection in the genome because it is fully connected. It is possible for this to happen naturally, but may be a sign of bad configuration')
            # If the re enabled flag was true though we can just return
            return

        # Get new innov_id, either by checking if this mutation has happened before in this generation, or by getting a new one
        innov_id = self.new_conn_signatures.get(pair)

        if innov_id == None:
            innov_id = self.get_next_conn_innov_num()
            self.new_conn_signatures[pair] = innov_id
        else:
            logging.debug(
                'Connection mutation has happened before this generation. Using old innovation number.')

        genotype.connection_genes.append(
            ConnectionGene(innov_id, pair[0], pair[1], 1.0))

    def similarity_operator(self, gen1: Genotype, gen2: Genotype) -> float:
        """Takes two genotypes and calculates their similarity

        Args:
            gen1 (Genotype): first genotype.
            gen2 (Genotype): second genotype.

        Returns:
            float: similarity score based on the hyper params:
                self.sim_disjoint_weight
                self.sim_excess_weight
                self.sim_weight_diff_weight
        """

        disjoint_conns, excess_conns, weight_diff_average = compare_connection_genes(
            gen1.connection_genes, gen2.connection_genes)

        # disjoint_nodes, excess_nodes = compare_node_genes(
        #     gen1.node_genes, gen2.node_genes)

        disjoints = disjoint_conns  # + disjoint_nodes
        excesses = excess_conns  # + excess_nodes

        normalisation_factor = max(
            len(gen1.connection_genes) + len(gen1.node_genes),
            len(gen2.connection_genes) + len(gen2.node_genes))
        if normalisation_factor > self.sim_genome_length_threshold:
            normalisation_factor = 1

        return (disjoints * self.sim_disjoint_weight) / normalisation_factor + \
            (excesses * self.sim_excess_weight) / normalisation_factor + \
            weight_diff_average * self.sim_weight_diff_weight

    def cycle_species(self):
        """Select a random member of each species to be the species representative for the next generation and reset their memberships
        """
        for species_id, species in self.species.items():
            species.cycle(self.neat_random)

    def place_into_species(self) -> None:
        """Place the the population into species or create a new one if not compatible

        Args:
            genotype (Genotype): Genotype to place into species
        """
        #
        for genotype in self.population:
            for species_id, species in self.species.items():
                assert species.prototype is not None
                if self.similarity_operator(species.prototype, genotype) <= self.sim_threshold:
                    species.add_member(genotype)
                    return

            # Create new species if none match
            new_species_num = self.get_next_species_number()
            new_species = Species(new_species_num, genotype)
            new_species.add_member(genotype)
            assert self.species.get(new_species_num) is None
            self.species[new_species_num] = new_species

            logging.info(f'Creating new species {new_species_num}')

        extinct: List[int] = []
        for species_id, species in self.species.items():
            if len(species.members) == 0:
                logging.info(f'Species {species.species_id} has died out')
                extinct.append(species.species_id)

        for species_id in extinct:
            del self.species[species_id]
