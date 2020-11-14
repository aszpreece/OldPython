from typing import Tuple
import unittest
from src.phenotype import calculate_execution_order


class TestCalculateExecutionOrder(unittest.TestCase):

    def test_calculate_execution_order(self):

        input_nodes = [1]
        non_input_nodes = [2, 3, 4, 5, 6]

        recurrent_connections = {6, 7}

        connection_dict: "dict[int, list[Tuple[int, float, int]]]" = {
            1: [],
            2: [(1, 0.1, 1), (5, 0.1, 8)],
            3: [(2, 0.1, 9), (6, 0.1, 5)],
            4: [(2, 0.1, 3), (3, 0.1, 4)],
            5: [(4, 0.1, 7)],
            6: [(2, 0.1, 2), (3, 0.1, 6)],
        }

        order = calculate_execution_order(
            input_nodes, non_input_nodes, recurrent_connections, connection_dict)

        self.assertListEqual(order, [5, 2, 6, 3, 4])
