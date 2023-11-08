from src.external_lib.searchGeneric import AStarSearcher


class MySearcher(AStarSearcher):
    """
    My searcher that use AStarMethod
    """

    def __init__(self, problem):
        super().__init__(problem)
