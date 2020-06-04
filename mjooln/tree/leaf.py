from mjooln import File, Segment


class LeafError(Exception):
    pass


class Leaf(File, Segment):
    """ Existing file within a tree that following segment naming."""

    def __init__(self, file):
        File.__init__(self)
        Segment.__init__(self, self.stub())

    def delete(self, missing_ok=False):
        raise LeafError('Cannot delete a Leaf')

