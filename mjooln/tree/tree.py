import logging

from mjooln import CryptError, Folder, File, Atom, AtomError
from mjooln.tree.root import Root, NotRootException
from mjooln.tree.leaf import Leaf, LeafError

logger = logging.getLogger(__name__)


class TreeError(Exception):
    pass


class NotTreeException(NotRootException):
    pass


class Tree(Root):
    """
    Folder structure based on strict :class:`.Atom` file names, and with an
    autonomous vocabulary.

    Create a new Tree by planting it in any folder, and with a key following
    the limitations of :class:`Key`::

        folder = Folder.home()
        key = 'oak'
        oak = Tree.plant(folder, key)

    Files outside the tree are defined as ``native``, while files in the
    tree are called ``Leaf``. Leaves are uniquely identified by
    :class:`.Atom`, which also defines their position in the folder
    structure underlying the tree.

    Leaves can be grown from a native file by defining a corresponding
    atom::

        native = File('some_outside_file.csv')
        atom = Atom(key='my_key')
        oak.grow(native, atom)

    The file may later be retrieved

    """

    #: Tree class identifier
    TREE = 'tree'

    #: Current class identifier (this is a Tree)
    SPECIES = TREE

    @classmethod
    def is_tree(cls, folder):
        """
        Check if folder is a tree

        :param folder: Folder to check
        :type folder: Folder
        :return: True if folder is a tree, False if not
        :rtype: bool
        """
        try:
            _ = cls(folder)
            return True
        except NotRootException:
            return False

    @classmethod
    def plant(cls, folder, key,
              extension='csv',
              compress_all=False,
              encrypt_all=False,
              key_level=None,
              date_level=0,
              time_level=0,
              encryption_key=None,
              **kwargs):
        """
        Creates a new tree

        Folder specifies where the tree should be planted, while key will
        be the name of the tree folder

        :param folder: Folder to plant the tree in
        :type folder: Folder
        :param key: Tree name or key
        :type key: Key
        :param extension: File extension for all files/leaves in tree
        :type extension: str
        :param compress_all: Flags compression of all files/leaves in tree
        :type compress_all: bool
        :param encrypt_all: Flags encryption of all files/leaves in tree
        :type encrypt_all: bool
        :param key_level: Key levels for folder structure
        :type key_level: int/None
        :param date_level: Date levels for folder structure
        :type date_level: int/None
        :param time_level: Time levels for folder structure
        :type time_level: int/None
        :param encryption_key: (*optional*) Encryption key used for
            encryption/decription of files/leaves in tree
        :type encryption_key: bytes
        :param kwargs: Additional attributes of tree
        :return: New tree
        :rtype: Tree
        """
        tree = super(Tree, cls).plant(folder, key,
                                      extension=extension,
                                      compress_all=compress_all,
                                      encrypt_all=encrypt_all,
                                      key_level=key_level,
                                      date_level=date_level,
                                      time_level=time_level,
                                      **kwargs)
        if encryption_key:
            tree.add_encryption_key(encryption_key)
        return tree

    def __init__(self, folder, encryption_key=None):
        self.extension = 'csv'
        self.compress_all = False
        self.encrypt_all = False
        self.key_level = None
        self.date_level = 0
        self.time_level = 0
        self._encryption_key = None
        super(Tree, self).__init__(folder)
        if self.species() != self.SPECIES:
            raise NotTreeException(f'Species mismatch. '
                                   f'Expected: {self.SPECIES}, '
                                   f'Found: {self.species()}')
        if encryption_key:
            self.add_encryption_key(encryption_key)

    def add_encryption_key(self, encryption_key=None):
        """
        Adds encryption key to trees with encryption activated. Encryption key
        may also be added in constructor. It will not be stored on disk, only
        in memory.

        :raise TreeError: If encryption is activated, but encryption_key is
            None
        :param encryption_key: Encryption key as defined by :class:`.Crypt`
        :type encryption_key: bytes
        """
        if self.encrypt_all and encryption_key is None:
            raise TreeError(f'Tree is encrypt_all, but no encryption_key '
                            f'supplied in constructor. Check Crypt class on '
                            f'how to make one, or disable encryption')
        self._encryption_key = encryption_key

    def _branch(self, atom):
        """
        Get the folder for the given atom

        :param atom: Input atom
        :type atom: Atom
        :return: Folder where a leaf with the input atom would be
        :rtype: Folder
        """
        levels = atom.levels(key_level=self.key_level,
                             date_level=self.date_level,
                             time_level=self.time_level)
        return self._folder.append(levels)

    def grow(self,
             native,
             atom=None,
             force_extension=False,
             delete_native=False):
        """
        Add a file to the tree. A file outside of the tree is called ``native``
        while a file in the tree is called ``leaf``

        :param native: File to add to the tree
        :type native: File
        :param atom: Atom defining the contents of the file, if the file name
            is not a valid atom string
        :type atom: Atom
        :param force_extension: Flags forcing file extension to be the
            extension inherent in tree
        :type force_extension: bool
        :param delete_native: Flags whether to delete the native file after
            file has been copied to the tree structure
        :type delete_native: bool
        :return: New leaf in tree
        :rtype: Leaf
        """
        native = File.elf(native)
        if not native.exists():
            raise TreeError(f'Cannot grow Leaf from non existent '
                            f'path: {native}')
        if not native.is_file():
            raise TreeError(f'Native is not a file: {native}')
        if not force_extension and len(native.extensions()) != 1:
            raise TreeError(f'Leaves must have one extension, this native '
                            f'has none or multiple: {native.extensions()}. '
                            f'Use force_extension to set it to '
                            f'tree inherent: \'{self.extension}\'')

        if not atom:
            try:
                atom = Atom(native.stub())
            except AtomError as se:
                raise TreeError(f'File name is not a valid '
                                f'atom: {native.name()}. '
                                f'Add atom as parameter to override '
                                f'file name.') from se

        if force_extension:
            extension = self.extension
        else:
            extension = native.extension()

        new_name = File.make_file_name(str(atom),
                                       extension,
                                       is_compressed=native.is_compressed(),
                                       is_encrypted=native.is_encrypted())

        if native.name() == new_name:
            new_name = None

        folder = self._branch(atom)
        if delete_native:
            file = native.move(folder, new_name)
        else:
            file = native.copy(folder, new_name)
        leaf = Leaf(file)
        logger.debug(f'Added leaf: {leaf}')
        leaf = self._shape(leaf)
        return leaf

    def leaf(self, atom):
        """
        Get the leaf defined by the given atom

        :param atom: Atom defining the leaf contents
        :type atom: Atom
        :return: Leaf defined by the atom
        :rtype: Leaf
        """
        atom = Atom.elf(atom)
        folder = self._branch(atom)
        file_name = File.make_file_name(str(atom),
                                        self.extension,
                                        is_compressed=self.compress_all,
                                        is_encrypted=self.encrypt_all)
        file = File.join(folder, file_name)
        return Leaf(file)

    def leaves(self):
        """
        Get a list of all leaves in tree

        :return: List of leaves in tree
        :rtype: [Leaf]
        """
        files = self._folder.files(recursive=True)
        leaves = []
        for file in files:
            try:
                leaves.append(Leaf(file))
            except (LeafError, AtomError, ValueError) as e:
                logger.warning(f'File is not leaf: {e}. '
                               f'Pruning is recommended')
        return leaves

    def _shape(self, leaf):
        """
        Performs compress/decompress and/or encrypt/decrypt on a given file
        to match tree settings

        :param leaf: Leaf to shape
        :type leaf: Leaf
        :return: Shaped leaf
        :rtype: Leaf
        """
        try:
            if not leaf.is_compressed() and self.compress_all:
                if leaf.is_encrypted():
                    leaf = leaf.decrypt(self._encryption_key)
                leaf = leaf.compress()
            elif leaf.is_compressed() and not self.compress_all:
                if leaf.is_encrypted():
                    leaf = leaf.decrypt(self._encryption_key)
                leaf = leaf.decompress()
            if not leaf.is_encrypted() and self.encrypt_all:
                leaf = leaf.encrypt(self._encryption_key)
            elif leaf.is_encrypted() and not self.encrypt_all:
                leaf = leaf.decrypt(self._encryption_key)
        except CryptError as ce:
            raise TreeError(f'Invalid or missing encryption key while '
                            f'attempting reshape of {leaf}. '
                            f'Original error: {ce}')

        return Leaf.elf(leaf)

    def reshape(self, **kwargs):
        """
        Changes folder structure and/or compress/encrypt settings for all
        files in the tree from the input keyword arguments

        Performs compress/decompress and/or encrypt/decrypt on all files in
        tree to match tree settings for is_compressed and is_encrypted.

        Also prunes the tree moving files to correct folders, and deleting
        unused folders according to level settings

        .. note:: Folder and key cannot be changed

        :raise TreeError: If kwargs contain ``folder`` or ``key``
        :param kwargs: Attributes to change. Allowed attributes as in
            :meth:`plant()`
        """
        if not kwargs:
            logger.debug('No input arguments. Skipping reshape.')
        else:
            if 'folder' in kwargs:
                raise TreeError('Cannot change the folder of a tree '
                                'with reshape')
            if 'key' in kwargs:
                raise TreeError('Cannot change the key of a tree with '
                                'reshape')
            self.add(kwargs)
            self.write()
            self.prune()

    def _prune_leaf(self, leaf):
        if not leaf.folder() == self._branch(leaf):
            leaf = leaf.move(self._branch(leaf))
            logger.debug(f'Move leaf: {leaf}')
        return leaf

    def prune(self, delete_not_leaf=False):
        """
        Moves files and deletes unused folders so that the tree structure
        matches level settings

        :param delete_not_leaf: Whether to delete files that are not leaf
        :type delete_not_leaf: bool
        """
        files = self._files()
        for file in files:
            try:
                leaf = Leaf(file)
                tmp = self._prune_leaf(leaf)
                _ = self._shape(tmp)
            except (AtomError, ValueError, LeafError):
                if delete_not_leaf:
                    logger.warning(f'Delete file that is not leaf: {file}')
                    file.delete()

        folders = self._folders()
        levels_and_folders = [(len(x.parts()), x) for x in folders]
        levels_and_folders.sort(reverse=True)
        for _, folder in levels_and_folders:
            if folder.is_empty():
                folder.remove()

    def _folders(self, pattern='*', recursive=True):
        paths = self._folder.folders(pattern=pattern, recursive=recursive)
        return [Folder(x) for x in paths]

    def _files(self, pattern='*', recursive=True):
        paths = self._folder.files(pattern=pattern, recursive=recursive)
        return [File(x) for x in paths]

    def weeds(self):
        """
        Scans the tree for files with invalid shape, folder or name

        :return: Dictionary of weeds
        :rtype: dict
        """
        # TODO: Move weeds output to a custom class
        leaves = self.leaves()
        files = self._files()
        not_leaves = len(files) - len(leaves)
        compression_mismatch = 0
        encryption_mismatch = 0
        for leaf in leaves:
            if leaf.is_compressed() != self.compress_all:
                compression_mismatch += 1
            if leaf.is_encrypted() != self.encrypt_all:
                encryption_mismatch += 1
        folders = self._folders()
        empty_folders = sum([x.is_empty() for x in folders])
        return {
            'not_leaves': not_leaves,
            'compression_mismatch': compression_mismatch,
            'encryption_mismatch': encryption_mismatch,
            'empty_folders': empty_folders,
            'total_weeds': not_leaves +
                           compression_mismatch +
                           encryption_mismatch +
                           empty_folders
        }

    def total_weeds(self):
        """
        Scan tree and count total number of invalid leaves (weeds)

        :return: Total number of weeds in tree
        :rtype: int
        """
        weeds = self.weeds()
        return weeds['total_weeds']
