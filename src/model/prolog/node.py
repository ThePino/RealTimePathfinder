import src.service.util as u


class Node:
    def __init__(self, id: str, lat: float, lon: float):
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
        distance_km = u.haversine_distance(self.lat, self.lon, node.lat, node.lon)
        return u.calculate_time(distance_km, speed_km)

    @classmethod
    def from_prolog_dictionary_result(cls, dictionary: dict) -> 'Node':
        """
        It returns a node from a prolog result query
        :param dictionary: The dictionary with all the keys
        :return: The node obtained
        """
        return Node(dictionary['Node'], float(dictionary['Lat']), float(dictionary['Lot']))
