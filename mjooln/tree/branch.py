import logging

from mjooln import Dic, Segment, Folder

from mjooln.tree.leaf import Leaf

logger = logging.getLogger(__name__)


class BranchError(Exception):
    pass


class Branch(list):

    def __init__(self, levels):
        super().__init__(levels)
        # TODO: Refactor to handle other than segment? Or use override for that?
        # TODO: If so go back to config input
        # self.key_levels = key_levels
        # self.date_levels = date_levels
        # self.time_levels = time_levels

if __name__ == '__main__':
    b = Branch(['a','b','c'])
    print(b)
    print(len(b))
    # def branches(self, segment):
    #     return segment.levels(**self.dic())
    #
    # def folder(self, segment):
    #     return Folder.join(self.branches(segment))
    #
    # def grow(self, source_file, delete_source=False):
    #     if not source_file.exists():
    #         raise BranchError(f'Cannot grow Leaf from non existent '
    #                           f'source file: {source_file}')
    #     segment = Segment(source_file.stub())
    #     folder = self.folder(segment)
    #     if delete_source:
    #         file = source_file.move(folder)
    #     else:
    #         file = source_file.copy(folder)
    #     return Leaf(file)
