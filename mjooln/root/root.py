import logging

from mjooln import Dic, Doc, File, Folder

logger = logging.getLogger(__name__)


class RootError(Exception):
    pass


class NotRootException(RootError):
    pass


# TODO: Rewrite root as file?
class Root(Doc):
    """
    Combination of a folder and a file that defines a particular spot in
    the file system.

    Root key follows limitations of class :class:`.Key`.
    If root key is ``julian``,
    the following triplet of rules define a folder as a valid Root:

    1. Folder path is ``../julian``
    2. Folder contains a JSON file with name ``.julian.json``. The file may
       be compressed, adding extension ``.gz``, or encrypted, adding
       extension ``.aes``
    3. JSON file contains a dictionary, where one top level key is ``_root``,
       and the contents of the key is of type :class:`.Segment`, where
       ``Segment.key=julian``

    This triplet defines a Root as valid independent of file system, database
    entry or configuration file entry, allowing it to be used as a standalone
    knot of data, identifiable by shape and not identity.

    The Root class also stores all attributes, except private, in the JSON
    file. The key ``_root`` is reserved for class private attributes.

    """
    # TODO: Add segment and species description. Also needs to be planted
    # TODO: Change key to name?

    # Override in child class
    SPECIES = 'root'

    @classmethod
    def plant(cls, ground, key, species=SPECIES, **kwargs):
        folder = ground.append(key)
        if folder.exists():
            raise RootError(f'Cannot plant root in existing folder: {folder}. '
                            f'Empty and remove folder first. '
                            f'Or use a different folder.')
        root = cls(folder, default=True)
        folder.create()
        root._key = key
        root._species = species
        root.add(kwargs)
        root.write()
        return root


    @classmethod
    def _file_name(cls, folder, compressed=False, encrypted=False):
        file_name = File._HIDDEN_STARTSWITH + \
                    folder.name() + \
                    File._EXTENSION_SEPARATOR + \
                    File._JSON_EXTENSION
        if compressed:
            file_name += File._EXTENSION_SEPARATOR + File._COMPRESSED_EXTENSION
        if encrypted:
            file_name += File._EXTENSION_SEPARATOR + File._CRYPT_EXTENSION
        return file_name

    @classmethod
    def plant_with_force(cls, folder, species=SPECIES,
                         compressed=False, encrypted=False, **kwargs):
        """Plants a root, ignoring existing folder and other usual requirements"""
        if compressed or encrypted:
            raise RootError('Compression and encryption are not implemented.')

        root = cls(folder, default=True)
        root._species = species
        root.add(kwargs)

        if root._file.exists():
            root._file.delete()
        if root._folder.exists():
            if not folder.is_empty():
                raise RootError('Folder is not empty. Cannot plant anything '
                                'here, as there are limits to the force '
                                'applied. Use uproot, and with_force=True, '
                                'then plant.')

        root.write()
        return root

    @classmethod
    def is_root(cls, folder):
        try:
            _ = cls(folder)
            return True
        except RootError:
            return False

    def __init__(self, folder_path,
                 compressed=False,
                 encrypted=False,
                 default=False):
        if compressed or encrypted:
            raise RootError('Compression and encryption are not implemented.')
        self._folder = Folder(folder_path)
        if not default and not self._folder.exists():
            raise NotRootException(f'Folder does not exists: {self._folder}')
        self._file = File.join(self._folder,
                               self._file_name(self._folder,
                                               compressed=compressed,
                                               encrypted=encrypted))
        if not default and not self._file.exists():
            raise NotRootException(f'Description file does not exist: {self._file}')
        if default:
            self._key = folder_path.name()
            self._species = self.SPECIES
        if not default:
            self.read()
            if self._key != self._folder.name():
                raise NotRootException(f'Key/folder mismatch. '
                                       f'key={self._key}, '
                                       f'folder={self._folder}, '
                                       f'file={self._file}')

    def write(self):
        dic = self.dic()
        dic['_key'] = self._key
        dic['_species'] = self._species
        self._file.write(dic)

    def read(self):
        self._add_dic(self._file.read(), ignore_private=False)

    def uproot(self, with_force=False, key=None):
        if len(self._folder.list()) > 1:
            if with_force:
                if key == self._key:
                    self._folder.empty()
                else:
                    raise RootError(f'Root folder ({self}) is not empty. '
                                    f'Enter root key as input to '
                                    f'uproot with force: key={self._key}')
            else:
                raise RootError(f'Root folder ({self}) is not empty. '
                                f'Uproot with force to empty it: '
                                f'with_force=True')
        if self._file.exists():
            self._file.delete()
        self._folder.remove()
