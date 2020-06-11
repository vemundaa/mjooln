import logging

from mjooln import Dic, Doc, File, Folder, Atom, FileError, Path

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
       containing a :class:`.Root.RootDic` with ``Atom.key = 'julian'``

    This triplet defines a Root as valid independent of file system, database
    entry or configuration file entry, allowing it to be used as a standalone
    knot of data, identifiable by shape and not identity.

    The Root class also stores all attributes, except private, in the JSON
    file. The key ``_root`` is reserved for class private attributes.
    """
    # TODO: Add atom and species description. Also needs to be planted
    # TODO: Change key to name?
    # TODO: Allow compression and encryption

    #: Root class identifier
    ROOT = 'root'

    #: Current class species (this is Root)
    SPECIES = ROOT

    _FILE_WILDCARD = f'{File.HIDDEN_STARTSWITH}*' \
                     f'{File.EXTENSION_SEPARATOR}{File.JSON_EXTENSION}'

    class RootDic(Dic):
        """
        Container for root specific variables:

        - :class:`.Atom`
        - ``species``
        """

        @classmethod
        def new(cls, key, species):
            return cls(Atom(key=key), species)

        def __init__(self, atom, species):
            self.atom = atom
            self.species = species


    @classmethod
    def is_root(cls, folder):
        """
        Checks if folder is a valid root

        :param folder: Folder to check
        :type folder: Folder
        :return: True if folder is root, False if not
        :rtype: bool
        """
        try:
            _ = cls(folder)
            return True
        except NotRootException:
            return False

    @classmethod
    def _append_if_root(cls, roots, folder):
        try:
            root = cls(folder)
            roots.append(root)
        except NotRootException:
            pass

    @classmethod
    def find_all(cls, folder):
        """
        Find all roots in folder

        :param folder: Folder to search
        :type folder: Folder
        :return: List of roots found in folder
        :rtype: [Root]
        """
        path = Path.elf(folder)
        paths = path.glob(cls._FILE_WILDCARD, recursive=True)
        roots = []
        for path in paths:
            if path.is_file():
                file = File.elf(path)
                folder = file.folder()
                if file.stub() == folder.name():
                    if cls.is_root(folder):
                        cls._append_if_root(roots, folder)

        return roots

    @classmethod
    def plant(cls, folder, key, **kwargs):
        """
        Create a new root in folder, with given key and kwargs

        :param folder: Folder where the root will be created
        :type folder: Folder
        :param key: Root key, following :class:`.Key` limitations
        :type key: Key
        :param kwargs: Attributes to add to root
        :return: Created root
        :rtype: Root
        """
        root_folder = Folder.elf(folder).append(key)
        if root_folder.exists():
            raise RootError(f'Cannot plant root in existing folder: '
                            f'{root_folder}. '
                            f'Empty and remove folder first. '
                            f'Or use a different key.')
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
        dic._root = cls.RootDic.new(folder.name(), cls.SPECIES)
        dic.add(kwargs)
        return dic.dic(ignore_private=False)

    @classmethod
    def elf(cls, folder, **kwargs):
        """
        Converts an existing folder to root, tolerating missing file but not
        invalid key. If a folder already is a valid root, it will be returned
        as root. The folder name must be a valid :class:`.Key`

        :raise RootError: If file already exists, but does not have the right
            key, or if it has an invalid format
        :param folder: Folder to convert to root
        :type folder: Folder
        :param kwargs: Attributes to add to root file
        :return: New or existing root
        :rtype: Root
        """
        if cls.is_root(folder):
            return cls(folder)

        folder = Folder.elf(folder)
        file = File.join(folder, cls._file_name(folder))

        if file.exists():
            try:
                dic = file.read()
                if isinstance(dic['_root'], Atom):
                    key = dic['_root'].key
                    if key == folder.name():
                        raise RootError(f'This seems to be a valid root, but '
                                        f'is_root said otherwise. Contact '
                                        f'the rather incompetent developer of '
                                        f'this module.')
                    else:
                        raise RootError(f'Root file already exists, but has '
                                        f'the wrong key. '
                                        f'Expected: key={folder.name()}, '
                                        f'Found: key={key}')
                else:
                    raise RootError(f'Root file already exists, but has '
                                    f'invalid format. Should be atom, but '
                                    f'contents is instead: {dic}')
            except FileError as fe:
                raise RootError(f'Root file exists, does not seem to be a '
                                f'valid JSON file. '
                                f'Original error from read: {fe}')
        else:
            folder.touch()
            file.write(cls._dic(folder, **kwargs))

        return cls(folder)

    def __init__(self, folder):
        self._root = None
        self._folder = Folder.elf(folder)
        if not self._folder.exists():
            raise NotRootException(f'Folder does not exists: {self._folder}')
        self._file = File.join(self._folder,
                               self._file_name(self._folder))
        if not self._file.exists():
            raise NotRootException(f'Description file does '
                                   f'not exist: {self._file}')
        self.read()
        if self.key() != self._folder.name():
            raise NotRootException(f'Key/folder mismatch. '
                                   f'key={self._root.key}, '
                                   f'folder={self._folder}, '
                                   f'file={self._file}')

    def write(self):
        """
        Write all root attributes to file
        """
        self.verify()
        if self.key() != self._folder.name():
            raise RootError(f'Cannot write the wrong root key to root file. '
                            f'Should be same as folder name: '
                            f'{self._folder.name()}, '
                            f'but is: {self.key()}')
        dic = self.dic()
        dic['_root'] = self._root
        self._file.write(dic)

    def read(self):
        """
        Read all root attributes from file
        """
        self._add_dic(self._file.read(), ignore_private=False)
        self._root = self.RootDic(**self._root)
        self.verify()

    def verify(self):
        """
        Verify that root is valid

        :raise NotRootException: If root is not valid
        """
        if self._folder.name() != self.key():
            raise NotRootException('Folder key mismatch')
        if self._file.stub() != self.key():
            raise NotRootException('File name key mismatch')

    def key(self):
        """
        Get root key

        :return: Root key
        :rtype: Key
        """
        return self._root.atom.key

    def zulu(self):
        """
        Get root zulu

        :return: Root zulu
        :rtype: Zulu
        """
        return self._root.atom.zulu

    def identity(self):
        """
        Get root identity

        :return: Root identity
        :rtype: Identity
        """
        return self._root.atom.identity

    def species(self):
        """
        Get root species

        :return: Root species
        :rtype: str
        """
        return self._root.species

    def folder(self):
        """
        Get root folder

        :return: Root folder
        :rtype: Folder
        """
        return self._folder

    # TODO: Add choice to remove root, but leave contents?
    def uproot(self, with_force=False, key=None):
        """
        Remove root. If root has contents, use ``with_force=True`` and
        ``key=<root key>`` to force this

        .. warning:: Forcing uproot will remove all contents recursively

        :param with_force: Flags forced uproot, which will remove all files
            and folders recursively
        :param key: Add key to verify forced uproot
        """
        if len(self._folder.list()) > 1:
            if with_force:
                if key == self.key():
                    self._folder.empty()
                else:
                    raise RootError(f'Root folder ({self}) is not empty. '
                                    f'Enter root key as input to '
                                    f'uproot with force: '
                                    f'key={self.key()}')
            else:
                raise RootError(f'Root folder ({self}) is not empty. '
                                f'Uproot with force to empty it: '
                                f'with_force=True')
        if self._file.exists():
            self._file.delete()
        self._folder.remove()
