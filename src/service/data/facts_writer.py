from src.service.data.osm_xml_parser import ParsingResult
from src.model.osm.node import Node
from src.model.osm.way import Way
from src.model.osm.way import OnewayOSMEnum
import logging


class FactsWriter:
    """
    The class that writes down the info parsed from the open street model and generates the event on the edges.
    """

    def __init__(self):
        logging.debug('FactsWriter service initialed.')

    def write_facts(self, data: ParsingResult, output_path: str):
        """
        It writes down the facts, on the given path, from the parsing of open street data and generated events.
        :param data: The data from the parsing
        :param output_path: The path to store the file
        :return:
        """
        logging.debug('Started writing facts..')
        node_dict = dict()
        for node in data.node_list:
            node_dict[node.id_node] = node

        with open(output_path, 'w') as f:
            node_ids = []
            # Writing nodes
            logging.debug('Writing node facts..')
            for node in data.node_list:
                self._write_node(f, node)
                node_ids.append(self._generate_node_id_fact(node))
            logging.debug('Writing node facts completed.')
            # Writing edges
            logging.debug('Writing way facts..')
            ways_ids = []
            for way in data.way_list:
                self._write_way(f, way, node_dict, ways_ids)
            logging.debug(f"Total number of ways {len(ways_ids)}")
            logging.debug('Writing way facts completed.')

            logging.debug('Writing event facts..')

        logging.debug('Writing facts finished.')

    def _write_fact(self, f, subject: str, attribute: str, value: str | float):
        """
        It writes on the file a fact
        :param f: The file on which write the fact
        :param subject: The subject of the fact
        :param attribute: The attribute of the fact
        :param value: The value of the fact
        :return:
        """
        f.write(f"prop({subject}, {attribute}, {value}).\n")

    def _write_node(self, f, node: Node):
        """
        It writes on the file the facts related to the open street map node.
        :param f: The file on which write the fact
        :param node: The node of which write the related fact
        :return:
        """
        node_id = self._generate_node_id_fact(node)
        self._write_fact(f, node_id, 'lat', str(node.lat))
        self._write_fact(f, node_id, 'lon', str(node.lon))
        self._write_fact(f, node_id, 'type', 'node')

    def _write_way(self, f, way: Way, node_dict: dict, ways_ids: list[str]):
        """
        It writes on the file the facts related to the open street way.
        :param f: The file on which write the facts
        :param way: The open street data way to write the facts about
        :param node_dict: The dictionary of the node present
        :param ways_ids: The list of all the ids generated from a single way of open street map
        :return:
        """
        edge_counter = 0
        for i in range(1, len(way.node_list)):
            from_node = node_dict.get(way.node_list[i - 1])
            to_node = node_dict.get(way.node_list[i])
            # Swapping the direction of the edge
            if way.get_type() == OnewayOSMEnum.IN_REVERSE_ORDER:
                from_node, to_node = to_node, from_node

            edge_counter = self._write_edge(f, way, from_node, to_node, edge_counter, ways_ids)
            if way.get_type() == OnewayOSMEnum.BIDIRECTIONAL:
                edge_counter = self._write_edge(f, way, to_node, from_node, edge_counter, ways_ids)

    def _write_edge(self, f, way: Way, from_node: Node, to_node: Node, edge_counter: int, way_ids: list[str]):
        way_id = self._generate_way_id_fact(way, edge_counter)
        self._write_fact(f, way_id, 'from_node', f"node{from_node.id_node}")
        self._write_fact(f, way_id, 'to_node', f"node{to_node.id_node}")
        self._write_fact(f, way_id, 'max_speed', way.get_max_speed())
        self._write_fact(f, way_id, 'available', 'true')
        self._write_fact(f, way_id, 'type', 'way')
        way_ids.append(way_id)
        return edge_counter + 1

    def _generate_node_id_fact(self, node: Node) -> str:
        """
        It generates the id for the fact for the given node
        :param node: The node to write the id
        :return: the string format
        """
        return f"node{node.id_node}"

    def _generate_way_id_fact(self, way: Way, edge_counter: int):
        """
        It generates the id for the fact for the given way
        :param way: The way to generate the fact
        :param edge_counter: The number of sub edge of the way
        :return:
        """
        return f"way{way.id_way}_{edge_counter}"
