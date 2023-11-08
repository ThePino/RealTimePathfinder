import logging

from src.service.prolog.pyswip_client import PySwipClient
from src.model.event.event import Event


class EventGenerator:
    """
    The interface that generate the event
    """

    def __init__(self, prolog: PySwipClient):
        self.prolog = prolog
        self.ways_id = self.prolog.ask_all_way_ids()
        self.state = dict()
        for way in self.ways_id:
            self.state[way] = True

    def update(self, time: int):
        raise NotImplementedError("Define a generating function that will be called after every cross")

    def get_time_to_wait_to_next_event(self, time):
        """
        The functions returns -1 if there is no time to wait for next event
        :param time:
        :return:
        """
        return -1

    def _change_status(self, way_id: str):
        """
        It changes the status for the given way
        :param way_id: The way to change the status
        :return:
        """
        value = True
        if self.state[way_id] == value:
            value = False
        self.state[way_id] = value
        self.prolog.set_available_attribute(way_id, value)


class NoEventGenerator(EventGenerator):
    """
    It does nothing
    """

    def __init__(self, prolog: PySwipClient):
        super().__init__(prolog)

    def update(self, time: int):
        return


class DefinedEventGenerator(EventGenerator):
    def __init__(self, prolog: PySwipClient, events: list[Event]):
        """
        It calls the event in a defined way.
        :param prolog: The client to modify the base knowledge
        :param way_ids: The list of ways ids to change the status for i-th call to generate.
        """
        super().__init__(prolog)
        self.events = events
        self.index = 0
        logging.debug('Event generator initiated')

    def update(self, time: int):
        """
        It updates the state of the edges by the time passed
        :param time:
        :return:
        """
        logging.debug('Updating events..')
        while self.index < len(self.events) and time >= self.events[self.index].time:
            event = self.events[self.index]
            self._change_status(event.way_id)
            logging.debug(f"Event on time {event.time} on way {event.way_id}")
            self.index = self.index + 1
        logging.debug('Events updated.')

    def get_time_to_wait_to_next_event(self, time):
        """
        It returns the time to await for the next event
        :param time: The current time
        :return:
        """
        self.update(time)
        if self.index >= len(self.events):
            return -1
        return self.events[self.index].time - time
