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
    first_run: bool

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

    def __init__(self, base_genotype: Genotype, generation_size: int,  fitness_function: Callable[[Genotype], float],
                 neat_random=Random()) -> None:

        self.neat_random = neat_random
        self.first_run = True

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
        self.prob_to_split_connection = 0.05

        # Hyperparams for new connection mutation
        self.prob_to_connect_nodes = 0.05

        self.split_signatures = {}
        self.new_conn_signatures = {}

        self.generation_size = generation_size
        # Create initial population
        self.population = []
        for i in range(generation_size):
            self.population.append(copy.deepcopy(base_genotype))

        self.fitness_function = fitness_function
        self.fitness_scores = PriorityQueue(generation_size)

    def get_next_node_innov_num(self):
        self.node_innovation_number += 1
        return self.node_innovation_number

    def get_next_conn_innov_num(self):
        self.connection_innovation_number += 1
        return self.connection_innovation_number

    def mutate(self, genotype: Genotype):
        """Mutate the given genotype
        """
        if self.neat_random.uniform(0, 1) <= self.prob_to_mutate_weights:
            logging.info('Mutating weights')
            self.weight_mutate(genotype, self.neat_random)
        if self.neat_random.uniform(0, 1) <= self.prob_to_split_connection:
            logging.info('Splitting connection')
            self.split_connection_mutate(genotype, self.neat_random)
        if self.neat_random.uniform(0, 1) <= self.prob_to_connect_nodes:
            logging.info('Connecting unconnected nodes')
            self.add_connection_mutate(genotype, self.neat_random)

    def run_generation(self) -> Optional[Tuple[float, int]]:
        """Runs a generation and returns the score of the highest performing member

        Returns:
            float: [description]
        """
        # Base copies of new generation
        if not self.first_run:
            # Select best performing genomes from previous generation
            networks_to_take_forward = math.floor(
                self.percentage_top_networks_passed_on * self.generation_size)
            copies_per_network, remainder_to_fill = divmod(
                self.generation_size, networks_to_take_forward)

            new_population: List[Genotype] = []

            # Copy across one unmodified version of the best performing network
            _, index = self.fitness_scores.get()
            new_population.append(copy.deepcopy(self.population[index]))

            logging.debug(
                f'Copied across 1 unmodified copy of the best network, {remainder_to_fill + copies_per_network - 1} mutated copies of the best network and {copies_per_network * (networks_to_take_forward - 1)} mutated versions of other networks')

            # As it is possible the size of population may not divide cleanly, fill those remainder slots with mutated copies of the best network
            # As well as the copies of the best network that would already be added
            for i in range(remainder_to_fill + copies_per_network - 1):
                _, index = self.fitness_scores.get()
                genome_copy = copy.deepcopy(self.population[index])
                self.mutate(genome_copy)
                new_population.append(genome_copy)

            # Fill rest of population with copies of the rest of the good performing networks
            for i in range(networks_to_take_forward - 1):
                _, index = self.fitness_scores.get()
                for i in range(copies_per_network):
                    genome_copy = copy.deepcopy(self.population[index])
                    self.mutate(genome_copy)
                    new_population.append(genome_copy)

            del(self.population)
            self.population = new_population

        else:
            self.first_run = False

        self.split_signatures = {}
        self.new_conn_signatures = {}
        self.fitness_scores = PriorityQueue()

        highest_performer: Optional[Tuple[float, int]] = None

        for index, network in enumerate(self.population):

            score = self.fitness_function(network)

            # Place the score of the network and its index in the scores queue
            self.fitness_scores.put(
                (score, index))

            if highest_performer == None or score < highest_performer[1]:
                highest_performer = (score, index)

        return highest_performer

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

                connection_gene.weight += (random.random() * 2.0 - 1.0) * \
                    self.weight_perturb_scale
            else:
                # Assign a new random from a normal distribution
                connection_gene.weight = random.normalvariate(
                    0, self.new_weight_variance)

        for node_gene in genotype.node_genes:

            if node_gene.type != NodeType.INPUT:
                if random.uniform(0, 1) < self.prob_perturbing_weights:
                    # Perturb the weights
                    node_gene.bias += (random.random() * 2.0 - 1.0) * \
                        self.weight_perturb_scale
                else:
                    # Assign a new random from a normal distribution
                    node_gene.bias = random.normalvariate(
                        0, self.new_weight_variance)

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
        else:
            node_innov_id = self.get_next_node_innov_num()
            from_innov_id = self.get_next_conn_innov_num()
            to_innov_id = self.get_next_conn_innov_num()
            # Post the created innovation numbers as a tuple
            self.split_signatures[originalConnection.innov_id] = (
                node_innov_id, from_innov_id, to_innov_id)

        # Create a new node with a the innovation number
        genotype.node_genes.append(NodeGene(node_innov_id,
                                            NodeType.HIDDEN, bias=0))

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

        # We cannot connect 'to' input nodes so we should ignore them
        secondList = dict(
            (genotype.node_genes[i].innov_id, None) for i in indexes if genotype.node_genes[i].type != NodeType.INPUT)

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
                'Mutation has happened before. Using old innovation number.')

        genotype.connection_genes.append(
            ConnectionGene(innov_id, pair[0], pair[1], 1.0))
