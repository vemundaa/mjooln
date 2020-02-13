import logging

from mjooln import Root, Segment

logger = logging.getLogger(__name__)

# TODO: Tree should handle the different trees
# TODO: Separate branch class to handle the subfolder thing only from segments
# TODO: It should not be necessary to use segments in file names. Should have key as well. IE regular name
# TODO: A tree can also be flat. IE no branches.
# TODO: Tree has a root (file, mongo or other), branch (levels or none) and leaf (csv, h5, json, text, other)
# TODO: A regular file has only key and name.
# TODO: Segment file has specific name.
# TODO: Branch handles key or segment_key


class Tree(Root):

    @classmethod
    def plant(cls, folder,
              type='tree',
              compression=False,
              encryption=False,
              key_levels=1,
              date_levels=1,
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
        self.compression = False
        self.encryption = False
        self.key_levels = 1
        self.date_levels = 1
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
        segment = Segment(source_file.stub())
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