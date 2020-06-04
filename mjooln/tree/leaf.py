from mjooln import File, Atom


class LeafError(Exception):
    pass


class Leaf(File, Atom):
    """ Existing file within a tree that following atom naming."""

    def __init__(self, file):
        File.__init__(self)
        Atom.__init__(self, self.stub())
        if not self.exists():
            raise LeafError(f'Leaf path does not exist: {self}')
