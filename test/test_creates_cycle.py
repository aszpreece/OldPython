import unittest
from src.neat.genotype import ConnectionGene
from src.neat.phenotype import creates_cycle


class TestCreatesCycle(unittest.TestCase):

    def test_creates_1_step_cycle(self):
        # Test connection dictionary
        conn_dict = {
            2: [(1, 0.1, 100)],
        }

        conn_gene = ConnectionGene(innov_id=102, source=2, to=1, weight=0.1)

        recurrents = set()

        cycle = creates_cycle(conn_gene, conn_dict, recurrents)

        self.assertTrue(cycle)

    def test_creates_2_step_cycle(self):
        # Test connection dictionary
        conn_dict = {
            2: [(1, 0.1, 100)],
            3: [(2, 0.1, 101)],
        }

        conn_gene = ConnectionGene(innov_id=102, source=3, to=1, weight=0.1)

        recurrents = set()

        cycle = creates_cycle(conn_gene, conn_dict, recurrents)

        self.assertTrue(cycle)

    def test_not_creates_cycle(self):
        # Test connection dictionary
        conn_dict = {
            2: [(1, 0.1, 100)],
            3: [(2, 0.1, 101)],
        }

        # We haven't seen 5 before so this shouldn't create any cycles
        conn_gene = ConnectionGene(innov_id=102, source=3, to=5, weight=0.1)

        recurrents = set()

        cycle = creates_cycle(conn_gene, conn_dict, recurrents)

        self.assertFalse(cycle)

    def test_ignores_recurrent(self):
        # Test connection dictionary

        # Read it as "2 has a link sourced from 1"
        conn_dict = {
            2: [(1, 0.1, 100)],
            3: [(2, 0.1, 101)],
            4: [(3, 0.1, 102)],
        }

        # Firstly, an extra test to make sure the addition of the connection we are looking
        # to be marked as recurrent would be
        conn_gene = ConnectionGene(innov_id=103, source=4, to=1, weight=0.1)
        recurrents = set()
        cycle = creates_cycle(conn_gene, conn_dict, recurrents)
        self.assertTrue(cycle)

        # Add the connection
        conn_dict[1] = [(4, 0.1, 103)]
        # Add it to the recurrents set
        recurrents.add(103)

        # Now we are going to add a new connection FROM 2 TO 4
        # This connection isn't recurrent as it doesn't create any cycles on its own,
        # BUT only if the algorithm properly ignores the recurrent connection FROM 4 TO 1

        conn_gene = ConnectionGene(innov_id=104, source=2, to=4, weight=0.1)
        cycle = creates_cycle(conn_gene, conn_dict, recurrents)
        self.assertFalse(cycle)
