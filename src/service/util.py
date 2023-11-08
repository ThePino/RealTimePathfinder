import math

def calculate_time(distance_km: float, speed_km: float) -> int:
    """
    It calculates the number of second needed to do the specified amount of km in the specified velocity.
    :param distance_km: The distance
    :param speed_km: The velocity
    :return: The number of seconds to do the specified amount of space with the given velocity
    """
    return int(distance_km / speed_km) * 3600


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    It calculates the distance in km of 2 points from lattitue and longitude
    :param lat1: lattitude of the first point
    :param lon1: longitude of the first point
    :param lat2: lattitude of the second point
    :param lon2: longitude of the second point
    :return: The distance in km
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    radius = 6371  # Radius of the Earth in kilometers
    distance = radius * c
    return distance
