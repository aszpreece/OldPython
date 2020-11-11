import networkx as nx
import matplotlib.pyplot as plt

from src.genotype import Genotype, NodeType


def CreateGraph(genome: Genotype):

    G = nx.DiGraph()

    node_cols = {
        NodeType.INPUT: {"color": "blue"},
        NodeType.HIDDEN: {"color": "green"},
        NodeType.OUTPUT: {"color": "red"}
    }

    G.add_nodes_from([(node.id, node_cols[node.type])
                      for node in genome.node_genes])

    G.add_weighted_edges_from([(con.source, con.to, con.weight)
                               for con in genome.connection_genes])

    plt.subplot(121)
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.show()
