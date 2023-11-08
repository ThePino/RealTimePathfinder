from xml.etree.ElementTree import Element


class Event:
    """
    The class that represents an event
    """
    def __init__(self, way_id: str, time: int):
        """

        :param way_id: The id of the way in the event
        :param time: The time in second on which the event has happened
        """
        self.way_id = way_id
        self.time = time

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        return self.time == other.time
    @classmethod
    def from_event_xml_element(cls, element: Element):
        """
        It generates an event from the xml element
        :param element: The xml element
        :return: The element
        """
        way_id = element.get('way')
        if way_id == "":
            way_id = None
        order_number = int(element.get('time'))
        return Event(way_id, order_number)
