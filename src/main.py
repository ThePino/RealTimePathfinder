import logging

from src.service.data.osm_xml_parser import OSMXmlParser
from src.service.data.facts_writer import FactsWriter
from src.service.data.event_xml_parser import EventXMLParser
from src.service.prolog.pyswip_client import PySwipClient
from src.service.handler import Handler
from src.service.event.event_generator import DefinedEventGenerator
from src.model.prolog.node import Node
from src.model.event.event import Event
import sys

class Environment:
    """
    The class that store all the enviroment variabile for the run of the application
    """
    def __init__(self, path_to_prolog_facts: str, path_to_prolog_rules: str,
                 path_to_xlm_event: str, path_to_osm_data: str,
                 from_node_id: str | None, to_node_id: str | None):
        self.path_to_prolog_facts = path_to_prolog_facts
        self.path_to_prolog_rules = path_to_prolog_rules
        self.path_to_xlm_event = path_to_xlm_event
        self.path_to_osm_data = path_to_osm_data
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id


def main(env: Environment):
    """
    The entry point of my application
    :param env: The environment variables
    :return:
    """
    # Bootstrapping the application
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Application started.")
    logging.debug("Initiating internal services..")
    # Initiating services
    parser_osm = OSMXmlParser()
    parser_event = EventXMLParser()
    writer = FactsWriter()
    # Path to the file
    _update_facts_file(env.path_to_osm_data, parser_osm, env.path_to_prolog_facts, writer)
    prolog_client = PySwipClient(env.path_to_prolog_facts, env.path_to_prolog_rules)
    events = _import_event_file(env.path_to_xlm_event, parser_event)
    # Picking up nodes
    nodes = prolog_client.ask_all_node()
    from_node = _find_node_by_id(nodes, env.from_node_id)
    to_node = _find_node_by_id(nodes, env.to_node_id)
    # Finding the pair of nodes to l
    if from_node is None or to_node is None:
        from_node, to_node = _find_longest_pair_of_node(nodes)
    assert _is_connected(from_node, to_node, prolog_client), 'The two nodes are not connected'

    event_generator = DefinedEventGenerator(prolog_client, events)
    handler = Handler(from_node, to_node, prolog_client, event_generator)

    final_path, time_passed = handler.run()
    logging.info(
        f"Number of traversal {len(final_path) - 1}, node traversal {final_path}, time passed in seconds {time_passed}")
    logging.info("Application has been shutdown")


def _update_facts_file(path_to_osm_data: str, parser: OSMXmlParser, path_to_prolog_facts: str, writer: FactsWriter, ):
    """
    A subroutine to parse data from the open street model and store the facts related on a file
    :param path_to_osm_data: The path of the file of the open street model
    :param parser: The parser of the xml
    :param path_to_prolog_facts: The path to store the prolog facts
    :param writer: The class that writes the facts on file
    :return:
    """
    logging.info(f"Importing open street data from:'{path_to_osm_data}'..")
    result = None
    with open(path_to_osm_data, 'r', encoding='utf-8') as file:
        result = parser.parse_osm_xml(file)
    logging.info('Imported open street data completed.')
    assert result is not None, 'A parsing result should be produced'
    writer.write_facts(result, path_to_prolog_facts)
    return


def _is_connected(nodeA: Node, nodeB: Node, prolog: PySwipClient) -> bool:
    """
    Checks if there is a path from nodeA to nodeB
    :param nodeA: the first node to check
    :param nodeB: the second node to check
    :return: True if the 2 nodes are connected
    """
    q = [nodeA]
    visited = set()
    visited.add(nodeA)
    while len(q) != 0:
        node = q[-1]
        q.pop()
        for edge in prolog.ask_all_available_from_node(node.id):
            if edge.node.id not in visited:
                visited.add(edge.node.id)
                q.append(edge.node)
                if edge.node == nodeB:
                    return True
    return False


def _import_event_file(path_to_event_data: str, parser: EventXMLParser) -> list[Event]:
    """
    It parses the events from the xml data
    :param path_to_event_data: The path to the xml file
    :param parser: The parser to prase the data with
    :return:
    """
    result = []
    with open(path_to_event_data, 'r', encoding='utf-8') as file:
        result = parser.parse_event_xml(file)
    return result


def _find_node_by_id(nodes: list[Node], node_id: str) -> Node | None:
    """
    Returns the node with the given id
    :param nodes: The array of nodes
    :param node_id: The node if needed
    :return: The node with the given id or None if nothing has been found
    """
    for node in nodes:
        if node.id == node_id:
            return node
    return None


def _find_longest_pair_of_node(nodes: list[Node]) -> list[Node]:
    """
    It finds the two far away nodes
    :param nodes: The array of nodes
    :return: The couple of nodes
    """
    assert len(nodes) >= 2, 'There should be at least two element to get a pair'
    logging.debug('Finding the pair of nodes with maximum distance..')
    from_node, to_node, distance = None, None, -1
    for i in range(0, len(nodes)):
        for j in range(i + 1, len(nodes)):
            if nodes[i].time_to_travel(nodes[j], 50) > distance:
                from_node, to_node = nodes[i], nodes[j]
    logging.debug('Found the pair of nodes')
    return from_node, to_node


if __name__ == "__main__":
    """
    Setting up environment variable
    """
    prolog_facts_path_main = '../resources/prolog/facts.pl'
    prolog_rules_path_main = '../resources/prolog/rules.pl'
    open_street_data_path_test = '../resources/open_street_map/test.osm'
    open_street_data_path_main = '../resources/open_street_map/vatican.osm'
    event_data_path_test = '../resources/event/event_test.xml'
    event_data_path_main = '../resources/event/event.xml'
    from_node_id_test = 'node3'
    to_node_id_test = 'node10'
    from_node_id_main = None
    to_node_id_main = None
    env_test = Environment(prolog_facts_path_main, prolog_rules_path_main,
                           event_data_path_test, open_street_data_path_test,
                           from_node_id_test, to_node_id_test)
    env_main = Environment(prolog_facts_path_main, prolog_rules_path_main,
                           event_data_path_main, open_street_data_path_main,
                           from_node_id_main, to_node_id_main)
    main(env_main)
