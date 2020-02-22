import logging

from mjooln import Doc, File, Folder

logger = logging.getLogger(__name__)


class RootError(Exception):
    pass


class NotARootException(RootError):
    pass


# TODO: Rewrite root as file?
class Root(Folder, Doc):
    """ Combination of a folder and a file that defines a particular spot in the file system.

    A root with name "julian", has a folder with the path ../julian, and in this
    folder is a file with the name .julian.json, containing root attributes.
    One of the attributes must be "key", and this attribute must equal "julian".

    Thus there is a triplet defining a particular folder as a valid root.

    There are three other default attributes:
     -
    """

    ROOT = 'root'
    SPECIES = ROOT

    @classmethod
    def _file_name(cls, folder):
        return '.' + folder.name() + '.json'

    @classmethod
    def _file(cls, folder):
        return File.join(folder, cls._file_name(folder))

    @classmethod
    def home(cls):
        return cls(Folder.home())

    @classmethod
    def plant(cls, folder, **kwargs):
        if folder.exists():
            raise RootError(f'Cannot plant root in existing folder: {folder}. '
                            f'Empty and remove folder first. Or use a different folder.')
        cls.plant_with_force(folder, **kwargs)

    @classmethod
    def plant_with_force(cls, folder, **kwargs):
        folder.touch()
        file = cls._file(folder)
        doc = Doc()
        doc.key = folder.name()
        if kwargs:
            doc._add_dic(kwargs)
        file.write(doc.doc())
        return cls(folder)

    @classmethod
    def is_root(cls, folder):
        try:
            _ = cls(folder)
            return True
        except RootError:
            return False

    @classmethod
    def elf(cls, folder, dic=None):
        if folder.exists():
            if cls._file(folder).exists():
                try:
                    return cls(folder)
                except RootError:
                    return None
            else:
                folder.remove()
                return cls.plant(folder, dic=dic)

        else:
            return cls.plant(folder, dic=dic)

    def __init__(self, folder):
        folder = Folder.elf(folder)
        if not folder.exists():
            raise NotARootException(f'Folder does not exists: {folder}')
        if not self._file(folder).exists():
            raise NotARootException(f'Description file does not exist: {self._file(folder)}')
        Folder.__init__(self)
        self.key = ''
        self.species = ''
        self.read()
        if self.key != folder.name():
            raise NotARootException(f'Key/folder mismatch. '
                                    f'key={self.key}, '
                                    f'folder={folder.name()}, '
                                    f'path={self}')

    def write(self):
        file = self._file(self)
        file.write(self.doc(), mode='w')

    def read(self):
        file = self._file(self)
        self._add_doc(file.read(mode='r'))

    def remove(self):
        file = self._file(self)
        file.delete()
        super().remove()

    def uproot(self, force=False, key=None):
        if not force and len(self.list()) > 1:
            raise RootError(f'Root is not empty: {self}. '
                            f'Use force=True')
        if force:
            if key == self.key:
                self.empty()
            else:
                raise RootError(f'Enter root key as input to '
                                f'force empty folder: {self.key}')
        self.remove()


if __name__ == '__main__':
    root_folder = Folder('/Users/vemundaa/dev/data/tenoone/test_tree4')
    print(root_folder)
    root = Root.plant(root_folder, hey='there')
    root.dev_print()
    root = Root(root_folder)
    root.dev_print()
    root.uproot()
