from pyswip import Prolog
from src.model.prolog.edge import Edge
from src.model.prolog.node import Node
import logging
import time


class PySwipClient:
    """
    The Client to interact with the knowledge base
    """

    def __init__(self, path_to_facts: str, path_to_rules: str):
        """
        :param path_to_facts: the path to the facts to import
        :param path_to_rules: the path to the rules to import
        """
        self.prolog = Prolog()
        self.prolog.consult(path_to_facts)
        self.prolog.consult(path_to_rules)
        logging.debug('Service PySwipClient initiated.')

    def ask_all_way_ids(self) -> list[str]:
        """
        It asks for all the ids of edges present
        :return: The list of ids of all the ways
        """
        result = self._query('get_all_way_ids(Way)')
        return list(map(lambda x: x['Way'], result))

    def ask_all_node(self) -> list[Node]:
        """
        It asks for all the ids of the nodes present
        :return: The list of ids of all the nodes
        """
        result = self._query('get_all_node(Node, Lat, Lot)')
        return list(map(lambda x: Node.from_prolog_dictionary_result(x), result))

    def ask_all_available_from_node(self, node_id: str) -> list[Edge]:
        """
        It asks for all the available ways from the given node
        :param node_id:
        :return: the list of nodes available
        """
        result = self._query(f"get_way_all_info_available({node_id}, To_node, To_node_lat, To_node_lon, Max_speed)")
        return list(map(lambda _: Edge.from_prolog_dictionary_result(_), result))

    def set_available_attribute(self, way_id: str, state: bool):
        """
        It changes the state of an edge
        :param way_id:
        :param state:
        :return:
        """
        value = 'true'
        if not state:
            value = 'false'
        return self._query(f"set_available_attribute({way_id}, {value})")

    def ask_speed_from_nodes(self, from_node:str, to_node:str) -> int|None:
        """
        It asks for the max speed between two nodes
        :param from_node:
        :param to_node:
        :return: The speed of the node. None if there is no way to cross
        """
        result = self._query(f"get_max_speed_from_nodes({from_node}, {to_node}, Max_speed)")
        if len(result) == 0:
            return None
        return int(result[0].get('Max_speed'))


    def _query(self, query):
        """
        It wraps up the result of the query and returns the list
        :param query: The query to launch
        :return:
        """
        logging.debug(f"Executing query on prolog: '{query}'..")
        start_time = time.time()
        query_result = self.prolog.query(query)
        return_value = list(query_result)
        logging.debug(f"item size: {len(return_value)}")
        query_result.close()
        end_time = time.time()
        logging.debug(f'Time passed in prolog query {end_time - start_time}s')
        return return_value
