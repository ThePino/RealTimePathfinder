# searchMPP.py - Searcher with multiple-path pruning
# AIFCA Python code Version 0.9.9 Documentation at http://aipython.org
# Download the zip file and read aipython.pdf for documentation

# Artificial Intelligence: Foundations of Computational Agents http://artint.info
# Copyright 2017-2023 David L. Poole and Alan K. Mackworth
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 4.0 International License.
# See: http://creativecommons.org/licenses/by-nc-sa/4.0/deed.en

from src.external_lib.searchGeneric import AStarSearcher, visualize
from src.external_lib.searchProblem import Path

class SearcherMPP(AStarSearcher):
    """returns a searcher for a problem.
    Paths can be found by repeatedly calling search().
    """
    def __init__(self, problem):
        super().__init__(problem)
        self.explored = set()

    def search(self):
        """returns next path from an element of problem's start nodes
        to a goal node. 
        Returns None if no path exists.
        """
        while not self.empty_frontier():
            self.path = self.frontier.pop()
            if self.path.end() not in self.explored:
                self.explored.add(self.path.end())
                self.num_expanded += 1
                if self.problem.is_goal(self.path.end()):
                    self.solution = self.path   # store the solution found
                    #self.display(1, f"Solution: {self.path} (cost: {self.path.cost})\n",
                    #self.num_expanded, "paths have been expanded and",
                    #        len(self.frontier), "paths remain in the frontier")
                    return self.path
                else:
                    #self.display(4,f"Expanding: {self.path} (cost: {self.path.cost})")
                    neighs = self.problem.neighbors(self.path.end())
                    #self.display(2,f"Expanding: {self.path} with neighbors {neighs}")
                    for arc in neighs:
                        self.add_to_frontier(Path(self.path,arc))
                    #self.display(3, f"New frontier: {[p.end() for p in self.frontier]}")
        #self.display(0,"No (more) solutions. Total of",
                    #self.num_expanded,"paths expanded.")


