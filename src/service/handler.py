import logging

from src.service.search.my_search_problem import MySearchProblem
from src.service.event.event_generator import EventGenerator
from src.model.prolog.node import Node
from src.service.prolog.pyswip_client import PySwipClient
from src.service.search.my_searcher import MySearcher
from typing import SupportsAbs


class Handler:
    """
    The service that simulate the path progress
    """

    def __init__(self, start_node: Node, end_node: Node, prolog: PySwipClient, event_generator: EventGenerator):
        """
        The initialization of the handler
        :param start_node: The starting node
        :param end_node: The goal node
        :param prolog: The prolog client
        :param event_generator: The event generator
        """
        self.start_node = start_node
        self.end_node = end_node
        self.prolog = prolog
        self.event_generator = event_generator

    def run(self) -> list[Node]:
        """
        The logic of the simulation idea
        :return:
        """
        logging.debug(f"Starting from {self.start_node}")
        end_path = [self.start_node]
        time = 0
        last_path, index = [], 2
        assert len(last_path) == 0, 'The list is not empty'
        while end_path[-1] != self.end_node:
            # Updating edges
            has_updated = self.event_generator.update(time)
            if has_updated:
                last_path, index = [], 2
            logging.debug(f'On node {end_path[-1]} at time {time}')
            # No old path nodes usable
            if index > len(last_path):
                problem = MySearchProblem(end_path[-1], self.end_node, self.prolog)
                searcher = MySearcher(problem)
                path = searcher.search()
                # There is no path, just wait
                if path is None:
                    time_to_wait, has_updated = self.event_generator.get_time_to_wait_to_next_event(time)
                    assert time_to_wait >= 0, 'A negative time returned, now way to get to the goal'
                    time += time_to_wait
                    end_path.append(end_path[-1])
                    # Resetting the path
                    last_path, index = [], 2
                    continue
                last_path = list(path.nodes())
                index = 2

            # Use the last path
            from_node = end_path[-1]
            to_node = last_path[-index]
            speed = self.prolog.ask_speed_from_nodes(from_node.id, to_node.id)
            if speed is None:
                time_to_wait, has_updated = self.event_generator.get_time_to_wait_to_next_event(time)
                assert time_to_wait >= 0, 'A negative time returned, now way to get to the goal'
                time += time_to_wait
                end_path.append(end_path[-1])
                # Resetting the path
                last_path, index = [], 2
                continue

            time_needed = (from_node.time_to_travel(to_node, speed))
            logging.debug(f'Found a way with speed {speed} and time to travel of {time_needed}' )
            time += time_needed
            end_path.append(to_node)
            index += 1

        return end_path, time

