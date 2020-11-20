
from collections import Set, deque
from typing import Deque, List, Tuple
from src.neat.genotype import ConnectionGene, NodeGene


def compare_connection_genes(genes1: List[ConnectionGene], genes2: List[ConnectionGene]) -> Tuple[int, int, float]:
    """Counts the disjoint and excess genes of two genomes and calculates the average weight difference between matching genes

    Args:
        genes1 (List[ConnectionGene]): Genome one.
        genes2 (List[ConnectionGene]): Genome two.

    Returns:
        Tuple[int, int, float]: Tuple of disjoint genes, excess genes and average weight difference
    """
    # Calculate number of similar genes

    gen1_genes_count = len(genes1)
    gen2_genes_count = len(genes2)

    gen1_index = 0
    gen2_index = 0

    disjoint_genes = 0

    weight_diff_count = 0
    shared_connections = 0

    while(gen1_index < gen1_genes_count and gen2_index < gen2_genes_count):
        gene1 = genes1[gen1_index]
        gene2 = genes2[gen2_index]

        if gene1.innov_id == gene2.innov_id:
            # genes match, progress both pointers
            gen1_index += 1
            gen2_index += 1
            weight_diff_count += abs(gene1.weight - gene2.weight)
            shared_connections += 1
            continue
        elif gene1.innov_id > gene2.innov_id:
            # If the conn1 (top genome) has a larger innovation number
            # Progress conn2s counter
            gen2_index += 1
            disjoint_genes += 1

            continue
        # This will always happen
        else:  # conn1.innov_id < conn2.innov_id
            # If the conn2 (bottom genome) has a larger innovation number
            # progress conn1s counter
            gen1_index += 1
            disjoint_genes += 1
            continue

    # Once we've got here we know some of the genes don't match so lets count them
    excess_genes = (gen1_genes_count - gen1_index) + \
        (gen2_genes_count - gen2_index)

    return (disjoint_genes, excess_genes, weight_diff_count / shared_connections)


def compare_node_genes(genes1: List[NodeGene], genes2: List[NodeGene]) -> Tuple[int, int]:
    """Counts the disjoint and excess genes of two genomes.

    Args:
        genes1 (List[ConnectionGene]): Genome one.
        genes2 (List[ConnectionGene]): Genome two.

    Returns:
        Tuple[int, int]: Tuple of disjoint genes and excess genes.
    """
    # Calculate number of similar genes

    gen1_genes_count = len(genes1)
    gen2_genes_count = len(genes2)

    gen1_index = 0
    gen2_index = 0

    disjoint_genes = 0

    while(gen1_index < gen1_genes_count and gen2_index < gen2_genes_count):
        gene1 = genes1[gen1_index]
        gene2 = genes2[gen2_index]

        if gene1.innov_id == gene2.innov_id:
            # genes match, progress both pointers
            gen1_index += 1
            gen2_index += 1
            continue
        elif gene1.innov_id > gene2.innov_id:
            # If the conn1 (top genome) has a larger innovation number
            # Progress conn2s counter
            gen2_index += 1
            disjoint_genes += 1

            continue
        # This will always happen
        else:  # conn1.innov_id < conn2.innov_id
            # If the conn2 (bottom genome) has a larger innovation number
            # progress conn1s counter
            gen1_index += 1
            disjoint_genes += 1
            continue

    # Once we've got here we know some of the genes don't match so lets count what we have left over
    excess_genes = (gen1_genes_count - gen1_index) + \
        (gen2_genes_count - gen2_index)

    return (disjoint_genes, excess_genes)
