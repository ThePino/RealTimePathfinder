from src.external_lib.searchMPP import SearcherMPP


class MySearcher(SearcherMPP):
    """
    My searcher that use AStarMethod
    """

    def __init__(self, problem):
        super().__init__(problem)
