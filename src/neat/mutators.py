import random
from src.neat.helper import compare_connection_genes, compare_node_genes
from numpy.testing._private.utils import assert_equal
from src.neat.phenotype import Phenotype
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

    fitness_scores: PriorityQueue

    generation_size: int

    sim_disjoint_weight: float
    sim_excess_weight: float
    sim_weight_diff_weight: float
    sim_genome_length_threshold: int

    sim_threshold: float
    species_index: int
    species_prototypes: Dict[int, Genotype]
    species_members_map: Dict[int, List[Genotype]]
    highest_performer: Optional[Tuple[float, int]]

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
        self.fitness_scores = PriorityQueue(self.generation_size)

        self.sim_disjoint_weight = 1.0
        self.sim_excess_weight = 1.0
        self.sim_weight_diff_weight = 0.3
        self.sim_genome_length_threshold = 20
        self.sim_threshold = 3.0

        self.species_index = 0
        self.species_prototypes = {0: base_genotype}
        self.species_members_map = {0: []}
        self.population = []
        self.highest_performer: Optional[Tuple[float, int]] = None

        for i in range(generation_size):
            genotype_copy = copy.deepcopy(base_genotype)
            self.population.append(genotype_copy)
            self.fitness_scores.put((1.0, i))
            self.species_members_map[0].append(genotype_copy)

    def get_next_node_innov_num(self):
        self.node_innovation_number += 1
        return self.node_innovation_number

    def get_next_conn_innov_num(self):
        self.connection_innovation_number += 1
        return self.connection_innovation_number

    def get_next_species_number(self):
        self.species_index += 1
        return self.species_index

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
        self.split_signatures = {}
        self.new_conn_signatures = {}
        self.species_members_map = {}

        # Select best performing genomes from previous generation
        networks_to_take_forward = math.floor(
            self.percentage_top_networks_passed_on * self.generation_size)
        copies_per_network, remainder_to_fill = divmod(
            self.generation_size, networks_to_take_forward)

        new_population: List[Genotype] = []

        # Copy across one unmodified version of the best performing network
        _, index = self.fitness_scores.get()
        unchanged_member = copy.deepcopy(self.population[index])
        self.place_into_species(unchanged_member)
        new_population.append(unchanged_member)

        logging.debug(
            f'Copied across 1 unmodified copy of the best network, {remainder_to_fill + copies_per_network - 1} mutated copies of the best network and {copies_per_network * (networks_to_take_forward - 1)} mutated versions of other networks')

        # As it is possible the size of population may not divide cleanly, fill those remainder slots with mutated copies of the best network
        # As well as the copies of the best network that would already be added
        for i in range(remainder_to_fill + copies_per_network - 1):
            _, index = self.fitness_scores.get()
            genome_copy = copy.deepcopy(self.population[index])
            self.mutate(genome_copy)
            self.place_into_species(genome_copy)
            new_population.append(genome_copy)

        # Fill rest of population with copies of the rest of the good performing networks
        for i in range(networks_to_take_forward - 1):
            _, index = self.fitness_scores.get()
            for i in range(copies_per_network):
                genome_copy = copy.deepcopy(self.population[index])
                self.mutate(genome_copy)
                self.place_into_species(genome_copy)
                new_population.append(genome_copy)

        self.population = new_population

        assert len(self.population) == self.generation_size

    def run_generation(self) -> Optional[Tuple[float, int]]:
        """Runs a generation and returns the score and id of the highest performing member in a pair

        Returns:
            [type]: [description]
        """
        self.set_species_prototypes()
        self.create_new_generation()

        self.fitness_scores = PriorityQueue()
        self.highest_performer = None

        for index, network in enumerate(self.population):

            score = self.fitness_function(network)
            network.fitness = score
            species_size = self.get_species_count(network.species_id)

            # Place the adjusted score of the network and its population index in the scores queue
            self.fitness_scores.put(
                (score / species_size, index))

            if self.highest_performer == None or score < self.highest_performer[0]:
                self.highest_performer = (score, index)

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

        disjoint_nodes, excess_nodes = compare_node_genes(
            gen1.node_genes, gen2.node_genes)

        disjoints = disjoint_conns + disjoint_nodes
        excesses = excess_conns + excess_nodes

        normalisation_factor = max(
            len(gen1.connection_genes) + len(gen1.node_genes),
            len(gen2.connection_genes) + len(gen2.node_genes))
        if normalisation_factor > self.sim_genome_length_threshold:
            normalisation_factor = 1

        return (disjoints * self.sim_disjoint_weight) / normalisation_factor + \
            (excesses * self.sim_excess_weight) / normalisation_factor + \
            weight_diff_average * self.sim_weight_diff_weight

    def set_species_prototypes(self):
        """Select a random member of each species to be the species representative for the next generation
        """

        self.species_prototypes = {}
        for species_id, member_list in self.species_members_map.items():
            self.species_prototypes[species_id] = random.choice(member_list)

    def place_into_species(self, genotype: Genotype) -> None:
        """Place the given genotype into a species or create a new one if non match
        Sets the species property on the genotype.
        Args:
            genotype (Genotype): Genotype to place into species
        """
        #
        for species_id, prototype in self.species_prototypes.items():
            if self.similarity_operator(prototype, genotype) <= self.sim_threshold:
                self.species_members_map.setdefault(
                    species_id, []).append(genotype)
                genotype.species_id = species_id
                # logging.info(f'Placed into old species {species_id}')

                return

        # Create new species if none match
        new_species_num = self.get_next_species_number()
        self.species_prototypes[new_species_num] = genotype
        self.species_members_map[new_species_num] = [genotype]
        genotype.species_id = new_species_num
        logging.info(f'Creating new species {new_species_num}')

    def get_species_fitness(self, id) -> float:
        # Loop through each species and calculate their fitness as a whole
        species_size = self.get_species_count(id)
        species_fitness_sum = 0
        for species_member in self.species_members_map[id]:
            species_fitness_sum == species_member.fitness

        return species_fitness_sum / species_size

    def get_species_count(self, id: int) -> int:
        """Get the amount of members a species has

        Args:
            id (int): Id of species to get count for

        Returns:
            int: Amount of members that species has
        """
        return len(self.species_members_map.get(id, []))
