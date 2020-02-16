import logging

from mjooln import Root, Segment, SegmentError

logger = logging.getLogger(__name__)


class Tree(Root):

    TREE = 'tree'
    SPECIES = TREE

    @classmethod
    def is_tree(cls, folder):
        file = cls._file(folder)
        if not file.exists():
            return False
        root = Root(folder)
        try:
            if root.species == cls.TREE

    @classmethod
    def plant(cls, folder,
              type=TREE,
              compression=None,
              encryption=None,
              key_levels=0,
              date_levels=0,
              time_levels=0,
              **kwargs):
        return super(Tree, cls).plant(folder,
                                      type=type,
                                      compression=compression,
                                      encryption=encryption,
                                      key_levels=key_levels,
                                      time_levels=time_levels,
                                      **kwargs)

    def __init__(self, folder):
        self.type = None
        self.compression = None
        self.encryption = None
        self.key_levels = 0
        self.date_levels = 0
        self.time_levels = 0
        super(Tree, self).__init__(folder)

    def branch(self, segment):
        levels = segment.levels(key_levels=self.key_levels,
                                date_levels=self.date_levels,
                                time_levels=self.time_levels)
        return self.append(levels)

    def grow(self, source_file, delete_source=False):
        if not source_file.exists():
            raise TreeError(f'Cannot grow Leaf from non existent '
                            f'source file: {source_file}')
        if not source_file.is_file():
            raise TreeError(f'Source is not a file: {source_file}')
        try:
            segment = Segment(source_file.stub())
        except SegmentError as se:
            raise TreeError(f'File name is not a valid segment: {source_file.name()}') from se

        folder = self.branch(segment)
        if delete_source:
            file = source_file.move(folder)
        else:
            file = source_file.copy(folder)
        logger.debug(f'Added leaf at: {file}')

    def reshape(self, wood):
        # TODO: IMplement
        # super().refactor(wood)
        self.prune()

    def prune(self):

        pass
    #     # TODO: Check path correct, and remove empty folders
    #     files = self.trunk.glob()
    #     for file in files:


class TreeError(Exception):
    pass


if __name__ == '__main__':
    from mjooln import Folder
    root_folder = Folder('/Users/vemundaa/dev/data/tenoone/test_tree4')
    print(root_folder)
    tree = Tree.plant(root_folder, hey='there')
    tree.dev_print()
    tree = Tree(root_folder)
    tree.dev_print()
    tree.uproot(force=True)
