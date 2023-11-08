import logging
import xml.etree.ElementTree as elementTree
import logging

from src.model.osm.node import Node
from src.model.osm.way import Way


class ParsingResult:
    """
    The result of parsing of the xml file
    """

    def __init__(self, node_list: list[Node], way_list: list[Way], min_lat: float, max_lat: float, min_lon: float,
                 max_lon: float):
        """
        :param node_list: The array of the nodes
        :param way_list: The list of the way
        :param min_lat: Minimum latitude of the nodes
        :param max_lat: Maximum latitude of the nodes
        :param min_lon: Minimum longitude of the nodes
        :param max_lon: Maximum longitude of the nodes
        """
        if node_list is None:
            node_list = []
        if way_list is None:
            way_list = []
        self.node_list = node_list
        self.way_list = way_list
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon


class OSMXmlParser:
    """
    The parser of the open street model xml
    """

    def __init__(self):
        logging.debug('OSMXmlParser service initialed.')

    def parse_osm_xml(self, file):
        """
        :param self:
        :param file: The file with
        :return:
        """
        logging.debug('Starting the parse of osm xml data..')
        tree = elementTree.parse(file)
        root = tree.getroot()
        logging.debug('Root of the data obtained.')

        # Parsing nodes
        node_dict = dict()
        logging.debug('Starting parsing of nodes..')
        for nodeElement in root.findall('node'):
            node = Node.from_osm_xml_element(nodeElement)
            node_dict.update({node.id_node: node})
        logging.debug('Parsing of nodes completed.')

        # Parsing ways
        logging.debug('Starting parsing of way..')
        ways = []
        for wayElement in root.findall('way'):
            way = Way.from_xlm_element(wayElement)
            ways.append(way)
        logging.debug('Parsing of way completed.')

        # Parsing boundaries
        logging.debug('Starting the parsing of boundaries..')
        bounds_element = tree.find('bounds')
        keys = ['minlat', 'maxlat', 'minlon', 'maxlat']
        min_lat, max_lat, min_lon, max_lon = (float(bounds_element.get(key)) for key in keys)
        logging.debug('Parsing of boundaries completed.')
        logging.debug('Completed of parsing of osm xml data.')

        # Filtering data

        logging.debug('Filtering unused data..')
        logging.debug(f'Number of node before filtering {len(node_dict)} number of ways {len(ways)}')
        node_refs = set()
        node_cnt = dict()
        drivable_ways = list(filter(lambda _: _.is_drivable(), ways))

        for w in drivable_ways:
            for node_id in w.node_list:
                if node_id not in node_cnt:
                    node_cnt[node_id] = 0
                node_cnt[node_id] = 1 + node_cnt[node_id]
            node_refs.add(w.node_list[0])
            node_refs.add(w.node_list[-1])


        for key, value in node_cnt.items():
            if value >= 2:
                node_refs.add(key)

        for w in drivable_ways:
            for n in w.node_list:
                node_refs.add(n)

        for w in drivable_ways:
            w.node_list = list(filter(lambda _: _ in node_refs, w.node_list))
            for i in range(0, len(w.node_list) - 1):
                if w.node_list[i] == w.node_list[i + 1]:
                    logging.error(f'Same node for way with id {w.id_way}')
                    assert not(w.node_list[i] == w.node_list[i + 1]), "Can't be same node"

        nodes = list(map(lambda id_node: node_dict.get(id_node), node_refs))
        logging.debug(f'Completed filtering of unused data. node found {len(nodes)}')
        return ParsingResult(nodes, drivable_ways, min_lat, max_lat, min_lon, max_lon)
