# TODO: Make leaf handle the different file types, and also how to load them from the given root
from mjooln import File, Segment, Doc
# from mjooln.tree.tree import Tree


class LeafError(Exception):
    pass


class Leaf(Segment, File, Doc):
    """ Existing file within a tree, and following segment naming."""

    @classmethod
    def default(cls):
        raise LeafError('Leaf does not have a default value')

    def __init__(self, file):
        # TODO: Segment as method instead of inheritance?
        Segment.__init__(self, file.stub())

    # def tree(self):
    #     # TODO: Check if this will possibly create numerous copies of same object.
    #     folder = self.folder()
    #     while not Tree.is_root(folder):
    #         folder = folder.parent()
    #         if folder.is_volume():
    #             raise LeafError(f'Leaf has no root: {self}')
    #     return Tree(folder)




if __name__ == '__main__':
    file = File(str(Segment(key='test')) + '.txt')
    print(file)
    l = Leaf(file)
    l.dev_print()
    #
    # def folder(self, file):
    #     extension = file.extension()
    #     if not extension == self.extension:
    #         raise LeafError(f'Invalid file extension. '
    #                         f'Tree has \'{self.extension}\'. '
    #                         f'File has: {file.extension()}')
    #     try:
    #         segment = Segment(file.stub())
    #     except SegmentError as se:
    #         raise LeafError(f'File stub must be valid segment. SegmentError {se}')
    #     return super().folder(segment)
    #
    # def elf(self, file, key=None, delete_after=True):
    #     folder = self.folder(file)
    #     if not folder == file.folder():
    #         file = self._add(folder, file, delete_after=delete_after)
    #     file = file.elfer(should_be_compressed=self.compressed,
    #                       should_be_encrypted=self.encrypted,
    #                       key=key)
    #     return file
    #
    # def add(self, file, delete_after=False):
    #     folder = self.folder(file)
    #     if self.compressed != file.is_compressed():
    #         raise LeafError(f'File/Tree compression mismatch. '
    #                         f'File compressed={file.is_compressed()}. '
    #                         f'Tree compressed={self.compressed}')
    #     if self.encrypted != file.is_encrypted():
    #         raise LeafError(f'File/Tree encryption mismatch. '
    #                         f'File encrypted={file.is_encrypted()}. '
    #                         f'Tree encrypted={self.encrypted}')
    #     return self._add(folder, file, delete_after=delete_after)
    #
    # def _add(self, folder, file, delete_after=False):
    #     if folder == file.folder():
    #         raise LeafError(f'File is already in correct folder in tree. Use elf().')
    #     else:
    #         tree_file = file.move(folder)
    #     if delete_after:
    #         file.delete()
    #     return tree_file


