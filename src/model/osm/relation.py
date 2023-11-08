from src.model.osm.tag_proprieties import TagProprieties


class Relation:
    """
    A class that represent a relation between object on osm
    """
    def __init__(self, related_object=None, tag_proprieties=None):
        """

        :param related_object: The object involved in this relationship
        :param tag_proprieties: The proprieties of this relationship
        """
        if tag_proprieties is None:
            tag_proprieties = TagProprieties()
        if related_object is None:
            related_object = []
        self.tag_proprieties = tag_proprieties
        self.related_object = related_object
