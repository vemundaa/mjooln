# TODO: Make leaf handle the different file types, and also how to load them from the given root
from mjooln import File, Segment


class LeafError(Exception):
    pass


class Leaf(File, Segment):
    """ Existing file within a tree that following segment naming."""

    def __init__(self, file):
        # TODO: Segment as method instead of inheritance?
        File.__init__(self)
        Segment.__init__(self, self.stub())

