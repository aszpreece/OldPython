
from src.neat.neat import NEAT
from typing import Dict, Optional, Tuple
from src.neat.node_type import NodeType
from src.neat.neat_config import NeatConfig
from src.neat.genotype import ConnectionGene, Genotype, NodeGene
import logging


class MutationManager:

    def cycle(self):
        pass

    def mutate(self, genotype: Genotype, config: NeatConfig):
        pass

    def get_next_node_innov_num(self):
        self.node_innovation_number += 1
        return self.node_innovation_number

    def get_next_conn_innov_num(self):
        self.connection_innovation_number += 1
        return self.connection_innovation_number


class DefaultMutationManager(MutationManager):

    def __init__(self) -> None:
        self.split_signatures = {}
        self.new_conn_signatures = {}

    def cycle(self):
        """Reset themutation manager so it is ready for a new generation
        """
        self.split_signatures = {}
        self.new_conn_signatures = {}

    def mutate(self, genotype: Genotype, config: NeatConfig):
        """Mutate the given genotype"""
        if config.neat_random.uniform(0, 1) <= config.prob_to_mutate_weights:
            self.weight_mutate(genotype, config.neat_random)
        if config.neat_random.uniform(0, 1) <= config.prob_to_split_connection:
            self.split_connection_mutate(genotype, config)
        if config.neat_random.uniform(0, 1) <= config.prob_to_connect_nodes:
            self.add_connection_mutate(genotype, config)

    def weight_mutate(self, genotype: Genotype, config: NeatConfig) -> None:
        """Given a genotype, mutate each weight.
        Weights have a chance of (1-self.chance_to_assign_random_weight) to have their weights perturbed by a scale of self.weight_perturb_scale.
        Weights have a chance of self.weight_perturb_scale to have their weight set to a random value.

        Args:
            genotype (Genotype): The genotype to mutate.
            random (Random): Instance of random to use.
        """

        for connection_gene in genotype.connection_genes:

            if config.neat_random.uniform(0, 1) < config.prob_perturbing_weights:
                # Perturb the weights
                connection_gene.weight += config.neat_random.uniform(-1, 1) * \
                    config.weight_perturb_scale
            else:
                connection_gene.weight = config.neat_random.uniform(
                    -1, 1) * config.new_weight_power

    def split_connection_mutate(self, genotype: Genotype, config: NeatConfig) -> None:
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

        # Disable the current connection
        originalConnection = config.neat_random.choice(enabledGenes)
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

    def add_connection_mutate(self, genotype: Genotype, config: NeatConfig) -> None:
        """Given a genotype, add a connection between two randomly selected previously unconnected nodes.
        The new connection will have a weight of 1.

        Args:
            genotype (Genotype): The genotype to mutate.
            random (Random): Instance of random to use.
        """

        # Shuffle two copies of the list of nodes. We can run through the first and attempt to pair it with a node from the second

        indexes = list(range(len(genotype.node_genes)))
        config.neat_random.shuffle(indexes)

        # Dictionaries guarantee preservation of insertion order.
        firstList = dict(
            (genotype.node_genes[i].innov_id, None) for i in indexes)

        config.neat_random.shuffle(indexes)

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
                if connection == None or connection.enabled == False:
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
            ConnectionGene(innov_id, pair[0], pair[1], config.neat_random.uniform(-1, 1) * config.new_weight_power))
