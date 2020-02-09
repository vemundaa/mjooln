import logging

from mjooln import Dic, Segment, Folder

from mjooln.tree.leaf import Leaf

logger = logging.getLogger(__name__)


class BranchError(Exception):
    pass


class Branch(Dic):

    def __init__(self, config):
        # TODO: Refactor to handle other than segment? Or use override for that?
        self.key_levels = 1
        self.date_levels = 0
        self.time_levels = 0
        if config:
            self.add_dic(config)

    def branches(self, segment):
        return segment.levels(**self.dic())

    def folder(self, segment):
        return Folder.join(self.branches(segment))

    def grow(self, source_file, delete_source=False):
        if not source_file.exists():
            raise BranchError(f'Cannot grow Leaf from non existent '
                              f'source file: {source_file}')
        segment = Segment(source_file.stub())
        folder = self.folder(segment)
        if delete_source:
            file = source_file.move(folder)
        else:
            file = source_file.copy(folder)
        return Leaf(file)









if __name__ == '__main__':
    b = Branch(test='ff', a=4)
    b = Branch()

    print(Branch.default())