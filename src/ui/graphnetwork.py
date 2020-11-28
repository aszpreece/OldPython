import networkx as nx
import matplotlib.pyplot as plt

from src.neat.genotype import Genotype, NodeType


def create_graph(genome: Genotype):

    G = nx.DiGraph()

    node_cols = {
        NodeType.INPUT: {"color": "blue"},
        NodeType.HIDDEN: {"color": "green"},
        NodeType.OUTPUT: {"color": "red"},
        NodeType.BIAS: {"color": "blue"},

    }

    G.add_nodes_from([(node.innov_id, node_cols[node.type])
                      for node in genome.node_genes])

    G.add_weighted_edges_from([(con.source, con.to, con.weight)
                               for con in genome.connection_genes if con.enabled])

    plt.subplot(121)
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.show()
