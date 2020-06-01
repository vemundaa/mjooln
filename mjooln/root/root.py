import logging

from mjooln import Dic, Doc, File, Folder, Path, Segment, FileError

logger = logging.getLogger(__name__)


class RootError(Exception):
    pass


class NotRootException(RootError):
    pass


class Root(Doc):
    """
    Combination of a folder and a file that defines a particular spot in
    the file system.

    .. warning:: Root is primarily meant to be used for inheritance, and
        not direct use

    Root key follows limitations of class :class:`.Key`.
    If root key is ``julian``,
    the following triplet of rules define a folder as a valid Root:

    1. Folder path is ``../julian``
    2. Folder contains a JSON file with name ``.julian.json``
    3. JSON file contains a dictionary, where one top level key is ``_root``,
       and the contents of the key is of type :class:`.Segment`, where
       ``Segment.key = 'julian'``

    This triplet defines a Root as valid independent of file system, database
    entry or configuration file entry, allowing it to be used as a standalone
    knot of data, identifiable by shape and not identity.

    The Root class also stores all attributes, except private, in the JSON
    file. The key ``_root`` is reserved for class private attributes.

    """
    # TODO: Add segment and species description. Also needs to be planted
    # TODO: Change key to name?

    ROOT = 'root'
    SPECIES = ROOT

    _FILE_WILDCARD = f'{File.HIDDEN_STARTSWITH}*' \
                     f'{File.EXTENSION_SEPARATOR}{File.JSON_EXTENSION}'

    @classmethod
    def find_all(cls, folder):
        folder = Folder.elf(folder)
        paths = folder.glob(cls._FILE_WILDCARD, recursive=True)
        roots = []
        for path in paths:
            if path.is_file():
                file = File.elf(path)
                folder = file.folder()
                if file.stub() == folder.name():
                    if cls.is_root(folder):
                        roots.append(Root(folder))

        return roots

    @classmethod
    def plant(cls, folder, key, **kwargs):
        root_folder = Folder.elf(folder).append(key)
        if root_folder.exists():
            raise RootError(f'Cannot plant root in existing folder: '
                            f'{root_folder}. '
                            f'Empty and remove folder first. '
                            f'Or use a different folder.')
        root_folder.create()
        file = cls._get_file(root_folder)
        file.write(cls._dic(root_folder, **kwargs))
        return cls(root_folder)

    @classmethod
    def _file_name(cls, folder):
        return cls._FILE_WILDCARD.replace('*', folder.name())

    @classmethod
    def _get_file(cls, folder):
        return File.join(folder, cls._file_name(folder))

    @classmethod
    def _dic(cls, folder, **kwargs):
        dic = Dic()
        dic._root = Segment(key=folder.name())
        dic._species = cls.SPECIES
        dic.add(kwargs)
        return dic.dic(ignore_private=False)

    @classmethod
    def elf(cls, folder, **kwargs):
        if cls.is_root(folder):
            return cls(folder)

        folder = Folder.elf(folder)
        file = File.join(folder, cls._file_name(folder))

        if file.exists():
            try:
                dic = file.read()
                if isinstance(dic['_root'], Segment):
                    key = dic['_root'].key
                    if key == folder.name():
                        raise RootError(f'This seems to be a valid root, but '
                                        f'is_root said otherwise. Contact '
                                        f'the incompetent developer of this '
                                        f'module.')
                    else:
                        raise RootError(f'Root file already exists, but has '
                                        f'the wrong key. '
                                        f'Expected: key={folder.name()}, '
                                        f'Found: key={key}')
                else:
                    raise RootError(f'Root file already exists, but has '
                                    f'invalid format. Should be segment, but '
                                    f'contents is instead: {dic}')
            except FileError as fe:
                raise RootError(f'Root file exists, does not seem to be a '
                                f'valid JSON file. '
                                f'Original error from read: {fe}')
        else:
            folder.touch()
            file.write(cls._dic(folder, **kwargs))

        return cls(folder)

    @classmethod
    def is_root(cls, folder):
        try:
            _ = cls(folder)
            return True
        except NotRootException:
            return False

    def __init__(self, folder):
        self._root = None
        self._species = None
        self._folder = Folder.elf(folder)
        if not self._folder.exists():
            raise NotRootException(f'Folder does not exists: {self._folder}')
        self._file = File.join(self._folder,
                               self._file_name(self._folder))
        if not self._file.exists():
            raise NotRootException(f'Description file does '
                                   f'not exist: {self._file}')
        self.read()
        if self._root.key != self._folder.name():
            raise NotRootException(f'Key/folder mismatch. '
                                   f'key={self._root.key}, '
                                   f'folder={self._folder}, '
                                   f'file={self._file}')

    def write(self):
        self.verify()
        if self._root.key != self._folder.name():
            raise RootError(f'Cannot write the wrong root key to root file. '
                            f'Should be same as folder name: '
                            f'{self._folder.name()}, '
                            f'but is: {self._root.key}')
        dic = self.dic()
        dic['_root'] = self._root
        dic['_species'] = self.SPECIES
        self._file.write(dic)

    def read(self):
        self._add_dic(self._file.read(), ignore_private=False)
        self.verify()

    def verify(self):
        if self._folder.name() != self.key():
            raise NotRootException('Folder key mismatch')
        if self._file.stub() != self.key():
            raise NotRootException('File name key mismatch')

    def key(self):
        return self._root.key

    def zulu(self):
        return self._root.zulu

    def identity(self):
        return self._root.identity

    def folder(self):
        return self._folder

    def uproot(self, with_force=False, key=None):
        if len(self._folder.list()) > 1:
            if with_force:
                if key == self._root.key:
                    self._folder.empty()
                else:
                    raise RootError(f'Root folder ({self}) is not empty. '
                                    f'Enter root key as input to '
                                    f'uproot with force: '
                                    f'key={self._root.key}')
            else:
                raise RootError(f'Root folder ({self}) is not empty. '
                                f'Uproot with force to empty it: '
                                f'with_force=True')
        if self._file.exists():
            self._file.delete()
        self._folder.remove()
