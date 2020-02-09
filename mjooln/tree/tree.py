from mjooln import Doc, Root

from mjooln.tree.branch import Branch
from mjooln.tree.leaf import Leaf


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
    def plant(cls,
              folder,
              branch=Branch.default()):
        instance = super(Tree, cls).plant(folder,
                                          branch=branch)
        return instance

    def __init__(self, folder):
        self.type = None
        self.branch = None
        super(Tree, self).__init__(folder)
        self.branch = Branch(self.branch)
    #
    # def grow(self, source_file, delete_source=False):
    #     return Leaf.grow(self, source_file, delete_source=delete_source)
    #
    # def folder(self, segment):
    #     branches = segment.branches(key_levels=self.key_levels,
    #                                 date_levels=self.date_levels,
    #                                 time_levels=self.time_levels)
    #     return self.branch(branches)

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
    from mjooln import Folder, Segment, TextFile
    from mjooln import Zulu
    f = Folder('/Users/vemundaa/dev/data/tenoone/tests/tree_test')
    try:
        t = Tree(f)
        t.up()
    except:
        pass
    tree = Tree.plant(f, key_levels=2, date_levels=1, time_levels=0)
    tree.dev_print()

    print(tree)
    zulus = Zulu.range()
    segs = [Segment(key='dummy__tester', zulu=x) for x in zulus]
    for s in segs:
        print(s)

    folders = [tree.folder(x) for x in segs]
    for p in folders:
        print(p)

    files = []
    for p,s in zip(folders, segs):
        pp = TextFile.join(p, str(s) + '.txt')
        f = TextFile.dev_create_sample(pp)
        files.append(f)
    # s = Segment(key='dummy_tester')
    # print(w.branch(s))
    # f = w.field()
    # print(f)

    tree.up(force=True)
