
import copy
from src.neat.neat import NEAT
from typing import Dict, Optional, Tuple
from src.neat.node_type import NodeType
from src.neat.neat_config import NeatConfig
from src.neat.genotype import ConnectionGene, Genotype, NodeGene
import logging


class MutationManager:

    def __init__(self,  initial_genome: Genotype) -> None:
        self.connection_innovation_number = max(
            map(lambda c: c.innov_id, initial_genome.connection_genes), default=0)
        self.node_innovation_number = max(
            map(lambda c: c.innov_id, initial_genome.node_genes))

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

    def __init__(self, initial_genome: Genotype) -> None:
        super().__init__(initial_genome)
        self.split_signatures = {}
        self.new_conn_signatures = {}

    def cycle(self):
        """Reset the mutation manager so it is ready for a new generation
        """
        self.split_signatures = {}
        self.new_conn_signatures = {}

    def mutate(self, genotype: Genotype, config: NeatConfig):
        """Mutate the given genotype"""
        if config.neat_random.random() < config.prob_to_split_connection:
            self.split_connection_mutate(genotype, config)
        elif config.neat_random.random() < config.prob_to_connect_nodes:
            self.add_connection_mutate(genotype, config)
        else:
            self.connection_mutate(genotype, config)

    def connection_mutate(self, genotype: Genotype, config: NeatConfig) -> None:
        """Given a genotype, mutate each weight.
        Weights have a chance of (1-self.chance_to_assign_random_weight) to have their weights perturbed by a scale of self.weight_perturb_scale.
        Weights have a chance of self.weight_perturb_scale to have their weight set to a random value.

        Args:
            genotype (Genotype): The genotype to mutate.
            random (Random): Instance of random to use.
        """

        for connection_gene in genotype.connection_genes:

            if config.neat_random.random() < config.prob_perturbing_weight:
                # Perturb the weights
                connection_gene.weight += config.get_weight_delta() * \
                    config.weight_perturb_scale

            if config.neat_random.random() < config.prob_reset_weight:
                connection_gene.weight = config.get_weight_delta() * config.new_weight_power

            if config.neat_random.random() < config.prob_enable_conn:
                connection_gene.enabled = True

            if config.neat_random.random() < config.prob_disable_conn:
                connection_gene.enabled = False

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
        # Fix: check if no connections

        if len(enabledGenes) == 0:
            return

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
            # logging.debug(
            #    'Split node has happened before this generation. Using old innovation numbers.')

        else:
            node_innov_id = self.get_next_node_innov_num()
            from_innov_id = self.get_next_conn_innov_num()
            to_innov_id = self.get_next_conn_innov_num()
            # Post the created innovation numbers as a tuple
            self.split_signatures[originalConnection.innov_id] = (
                node_innov_id, from_innov_id, to_innov_id)

        # Create a new node with the innovation number
        genotype.node_genes.append(NodeGene(node_innov_id,
                                            NodeType.HIDDEN, activation_func=config.neat_random.choice(config.activation_func)))

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
        proposed_gene: "Optional[ConnectionGene]" = None

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
                    proposed_gene = ConnectionGene(
                        self.connection_innovation_number + 1, first, second, config.get_weight_delta() * config.new_weight_power)
                    # Check if we can create this connection
                    cycle = genotype.creates_cycle(proposed_gene)
                    if cycle:
                        if not config.allow_recurrence:
                            proposed_gene = None
                            continue
                        else:
                            proposed_gene.recurrent = True
                    break

                # If there is a disabled connection we should re enable it TODO is this okay?
                elif connection.enabled == False:
                    # Check if re enabling this gene would cause a cycle

                    # Check if we can re enable this connection without causing a cycle
                    if not config.allow_recurrence and genotype.creates_cycle(connection):
                        continue
                    else:
                        # Flag that we have re enabled a gene
                        re_enabled_flag = True
                        connection.enabled = True
                        break

            else:
                # If this node is connected to everything then we cannot connect it to a new node and we must select a new 'first node
                continue
            break

        if proposed_gene == None:
            # Check if we re-enabled a connection instead
            if re_enabled_flag == False:
                # TODO
                # Unlikely (Famous last words), but we cannot do this mutation. We should log it
                logging.warn(
                    'Failed to create a new connection in the genome because it is fully connected. It is possible for this to happen naturally, but may be a sign of bad configuration')
            # If the re enabled flag was true though we can just return
            return

        # Get new innov_id, either by checking if this mutation has happened before in this generation, or by getting a new one
        signature = proposed_gene.source, proposed_gene.to

        innov_id = self.new_conn_signatures.get(signature)

        if innov_id == None:
            innov_id = self.get_next_conn_innov_num()
            self.new_conn_signatures[signature] = innov_id
        # else:
        #     logging.debug(
        #         'Connection mutation has happened before this generation. Using old innovation number.')

        proposed_gene.innov_id = innov_id

        genotype.connection_genes.append(proposed_gene)

    def crossover(self, g1: Genotype, g2: Genotype, config: NeatConfig) -> Genotype:

        fittest: Optional[Genotype] = None
        not_fittest: Optional[Genotype] = None

        if g1.fitness > g2.fitness:
            fittest = g1
            not_fittest = g2
        elif g1.fitness < g2.fitness:
            fittest = g2
            not_fittest = g1
        # If they match just pick one randomly
        else:
            if config.neat_random.random() < 0.5:
                fittest = g2
                not_fittest = g1
            else:
                fittest = g1
                not_fittest = g2

        baby = Genotype()

        baby.node_genes = copy.deepcopy(fittest.node_genes)
        baby.node_name_map = fittest.node_name_map

        fit_index = 0
        nfit_index = 0

        while fit_index < len(fittest.connection_genes) and nfit_index < len(not_fittest.connection_genes):
            fit_gene = fittest.connection_genes[fit_index]
            nfit_gene = fittest.connection_genes[nfit_index]

            if fit_gene.innov_id == nfit_gene.innov_id:
                # If they match inherit randomly
                if config.neat_random.random() < config.prob_inherit_from_fitter:
                    baby.connection_genes.append(copy.deepcopy(fit_gene))
                else:
                    baby.connection_genes.append(copy.deepcopy(nfit_gene))

                fit_index += 1
                nfit_index += 1
            elif fit_gene.innov_id > nfit_gene.innov_id:
                # Don't allow less fit parent to add extra genes
                nfit_index += 1
                continue
            elif fit_gene.innov_id < nfit_gene.innov_id:
                fit_index += 1
                # If this is a disjoint gene that the fitter parent has, add it.
                baby.connection_genes.append(copy.deepcopy(fit_gene))

        # Add remaining excess genes from fitter
        while fit_index < len(fittest.connection_genes):
            fit_gene = fittest.connection_genes[fit_index]
            baby.connection_genes.append(copy.deepcopy(fit_gene))
            fit_index += 1

        return baby
