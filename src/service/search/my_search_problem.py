from src.external_lib.searchProblem import Search_problem
from src.service.prolog.pyswip_client import PySwipClient
from src.model.prolog.node import Node
from src.model.prolog.edge import Edge
from src.external_lib.searchProblem import Arc
import math
import logging

class MySearchProblem(Search_problem):
    def __init__(self, from_node: Node, to_node: Node, pwswip_client: PySwipClient):
        self.from_node = from_node
        self.to_node = to_node
        self.pwsip_client = pwswip_client
        logging.info(f"Problem to solve from {from_node.id} to {to_node.id}")

    def start_node(self):
        return self.from_node

    def is_goal(self, node):
        return self.to_node == node

    def neighbors(self, node):
        edges = self.pwsip_client.ask_all_available_from_node(node.id)
        return list(map(lambda _: self._make_arc(node, _), edges))

    def heuristic(self, n):
        edge = Edge(self.to_node, 10)
        return self._make_arc(n, edge).cost

    def _make_arc(self, from_node: Node, edge: Edge):
        """
        It creates an arc from the given nodes
        :param from_node:
        :param edge: The edge with all the info
        :return:
        """
        return Arc(from_node, edge.node, from_node.time_to_travel(edge.node, edge.max_speed))


