import logging

import src.service.util as u


class Node:
    """
    The node returned by a prolog query
    """

    def __init__(self, id: str, lat: float, lon: float):
        """

        :param id: The id of the node
        :param lat: The lattitude of the node
        :param lon: The longitude of the node
        """
        self.id = id
        self.lat = lat
        self.lon = lon

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return (self.id == other.id
                and self.lat == other.lat
                and self.lon == other.lon)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '{' + f"id: {self.id}, lat: {self.lat}, lon: {self.lon}" + '}'

    def time_to_travel(self, node: 'Node', speed_km: int):
        """
        It calculates the amount of seconds needed to travel from one node to the another by the given speed in km
        :param node: The node to reach
        :param speed_km: The speed to travel
        :return: The amount of seconds needed to reach the given node
        """
        distance_km = u.haversine_distance(self.lat, self.lon, node.lat, node.lon)
        if distance_km == 0:
            logging.debug(f'nodes with distance 0 {self} and {node}')
        time = u.calculate_time(distance_km, speed_km)
        assert (time > 0 or (self == node)), 'Time should be positive if node different'
        return u.calculate_time(distance_km, speed_km)

    @classmethod
    def from_prolog_dictionary_result(cls, dictionary: dict) -> 'Node':
        """
        It returns a node from a prolog result query
        :param dictionary: The dictionary with all the keys
        :return: The node obtained
        """
        return Node(dictionary['Node'], float(dictionary['Lat']), float(dictionary['Lot']))
