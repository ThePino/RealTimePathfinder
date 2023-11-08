import xml.etree.ElementTree as elementTree
from src.model.event.event import Event
import logging


class EventXMLParser:
    def parse_event_xml(self, file) -> list[Event]:
        """
        It parses the event from the xml file
        :param file: The file to parse
        :return: The parsing element
        """
        logging.debug('Starting the parse of event xml data..')
        tree = elementTree.parse(file)
        root = tree.getroot()
        logging.debug('Root of the data obtained.')
        events = []
        for event_xml in root.findall('event'):
            events.append(Event.from_event_xml_element(event_xml))
        events.sort()
        return events
