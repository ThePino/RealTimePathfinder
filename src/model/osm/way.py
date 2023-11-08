import string
from enum import Enum
from xml.etree.ElementTree import Element
from src.model.osm.tag_proprieties import TagProprieties
import logging


class WayOSMEnum(Enum):
    """
    The class with the name of attributes and child for the way in the xml
    """

    NODE_REFERENCE = 'nd'
    """
    The tag of the sub-element of Way containing the reference of the node
    """

    ID = 'id'
    """
    The attribute of the tag Way containing the id
    """

    NODE_REFERENCE_REF = 'ref'
    """
    The name of the attribute of the tag for the reference of the node containing the id
    """


class HighwayOSMEnum(Enum):
    """
    The enum for the interested value for the key's tag highway
    """

    LIVING_STREET = 'living_street'
    """
    For living streets, which are residential streets where pedestrians have legal priority over cars.
    """

    MOTORWAY = 'motorway'
    """
    A restricted access major divided highway, normally with 2 or more running lanes plus emergency hard shoulder.
    """

    MOTORWAY_LINK = 'motorway_link'
    """
    The link roads leading to/from a motorway.
    """

    PATH = 'path'
    """
    A non-specific path.
    """

    PRIMARY = 'primary'
    """
    The next most important roads in a country's system, after trunks.
    """

    PRIMARY_LINK = 'primary_link'
    """
    The link roads leading to/from a primary road.
    """

    SERVICE = 'service'
    """
    For access roads to, or within an industrial estate, camp site, business park, car park etc.
    """

    TERTIARY = 'tertiary'
    """
    The next most important roads in a country's system, after secondary roads.
    """

    TERTIARY_Link = 'tertiary_link'
    """
    The link roads leading to/from a tertiary road.
    """

    TRACK = 'track'
    """
    Roads for mostly agricultural or forestry uses. If used in the context of a cycleway this means a cycle track running parallel to a road.
    """

    TRUNK = 'trunk'
    """
    The most important roads in a country's system that aren't motorways.
    """

    TRUNK_LINK = 'trunk_link'
    """
    The link roads leading to/from a trunk road.
    """

    UNCLASSIFIED = 'unclassified'
    """
    The least important through roads in a country's system.
    """


class OnewayOSMEnum(Enum):
    """
    The enum with the associated oneway value possible
    """

    BIDIRECTIONAL = 'no'
    """
    This is not a oneway street.
    """

    IN_ORDER = 'yes'
    """
    This is a oneway street, with the direction being the same order of the way nodes.
    """

    IN_REVERSE_ORDER = '-1'
    """
    This is a oneway street, with the direction being the reverse of the order of the way nodes.
    """


class Way:
    """
    The class representing a way on open street map
    """

    _HIGHWAY = 'highway'
    """
    The key of the attribute  highway that tells which street it it
    """

    _ONE_WAY = 'oneway'

    def __init__(self, id_way, node_list: list[int] = None, tag_proprieties=None):
        """
        :param id_way:
        :param node_list: the list of the id of the node in an ordered way
        :param tag_proprieties: The attributes of this way
        """
        if node_list is None:
            node_list = []
        if tag_proprieties is None:
            tag_proprieties = TagProprieties()
        self.id_way = id_way
        self.node_list = node_list
        self.tag_proprieties = tag_proprieties

    @classmethod
    def from_xlm_element(cls, node_element: Element):
        """
        It creates the Way from the xml element
        :param node_element:
        :return:
        """
        id_way = int(node_element.get(WayOSMEnum.ID.value))
        node_list = []
        for node_reference in node_element.findall(WayOSMEnum.NODE_REFERENCE.value):
            node_list.append(int(node_reference.get(WayOSMEnum.NODE_REFERENCE_REF.value)))
        tag_proprieties = TagProprieties.from_osm_xml_element(node_element)
        return cls(id_way, node_list, tag_proprieties)

    def is_drivable(self) -> bool:
        """
        Tells if the current way it's drivable for cars
        :return:
        """
        values = self.tag_proprieties.get(self._HIGHWAY)
        return len(set([_.value for _ in HighwayOSMEnum]) & values) > 0

    def get_type(self) -> OnewayOSMEnum:
        """
        Tells the type of the way. If no mapped it's found it will be treated as bidirectional
        :return: The type of the way of the street
        """
        way_type = OnewayOSMEnum.BIDIRECTIONAL
        set_value = self.tag_proprieties.get(self._ONE_WAY)
        if set_value is None or len(set_value) == 0:
            return way_type
        value = next(iter(set_value))
        if value == OnewayOSMEnum.BIDIRECTIONAL.value:
            value = OnewayOSMEnum.BIDIRECTIONAL
        if value == OnewayOSMEnum.IN_ORDER.value:
            value = OnewayOSMEnum.IN_ORDER.value
        if value == OnewayOSMEnum.IN_REVERSE_ORDER:
            value = OnewayOSMEnum.IN_REVERSE_ORDER
        return value

    def get_max_speed(self) -> int:
        """
        It returns the max speed for this way. If not specified, it returns 50 as the italian city street limit.
        :return:
        """
        speed = self.tag_proprieties.get('maxspeed')
        if speed is None or len(speed) == 0:
            return 50
        return int(next(iter(speed)))
