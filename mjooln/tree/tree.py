import logging
from mjooln import Root, NotRootException, Segment, SegmentError, \
    CryptError, Folder, File

from mjooln.tree.leaf import Leaf

logger = logging.getLogger(__name__)


class NotTreeException(NotRootException):
    pass


class Tree(Root):
    """
    Folder structure based on strict :class:`.Segment` file names, and with an
    autonomous vocabulary.

    Create a new Tree by planting it in any folder, and with a key following
    the limitations of :class:`Key`::

        folder = Folder.home()
        key = 'oak'
        oak = Tree.plant(folder, key)

    Files outside the tree are defined as ``native``, while files in the
    tree are called ``Leaf``. Leaves are uniquely identified by
    :class:`.Segment`, which also defines their position in the folder
    structure underlying the tree.

    Leaves can be grown from a native file by defining a corresponding
    segment::

        native = File('some_outside_file.csv')
        segment = Segment(key='my_key')
        oak.grow(native, segment)

    The file may later be retrieved

    """

    TREE = 'tree'
    SPECIES = TREE

    @classmethod
    def is_tree(cls, folder):
        try:
            _ = cls(folder)
            return True
        except NotRootException:
            return False

    @classmethod
    def plant(cls, folder, key,
              extension=None,
              compress_all=False,
              encrypt_all=False,
              key_level=None,
              date_level=0,
              time_level=0,
              encryption_key=None,
              **kwargs):

        tree = super(Tree, cls).plant(folder, key,
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
        self.compress_all = False
        self.encrypt_all = False
        self.key_level = None
        self.date_level = 0
        self.time_level = 0
        self._encryption_key = None
        super(Tree, self).__init__(folder)
        if self._species != self.SPECIES:
            raise NotTreeException(f'Species mismatch. '
                                   f'Expected: {self.SPECIES}, '
                                   f'Found: {self._species}')
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

    def branch(self, segment):
        levels = segment.levels(key_level=self.key_level,
                                date_level=self.date_level,
                                time_level=self.time_level)
        return self._folder.append(levels)

    def grow(self, native_file, segment=None, delete_source=True):
        # TODO: Add date parser option (use Zulu.parse) And assume tz
        if not native_file.exists():
            raise TreeError(f'Cannot grow Leaf from non existent '
                            f'path: {native_file}')
        if not native_file.is_file():
            raise TreeError(f'Native is not a file: {native_file}')

        if segment:
            new_name = native_file.name().replace(native_file.stub(),
                                                  str(segment))
        else:
            new_name = None
            try:
                segment = Segment(native_file.stub())
            except SegmentError as se:
                raise TreeError(f'File name is not a valid '
                                f'segment: {native_file.name()}. '
                                f'Add segment as parameter to override '
                                f'file name.') from se
        folder = self.branch(segment)
        if delete_source:
            file = native_file.move(folder, new_name)
        else:
            file = native_file.copy(folder, new_name)
        leaf = Leaf(file)
        logger.debug(f'Added leaf: {leaf}')
        leaf = self.shape(leaf)
        return leaf

    def leaf(self, segment):
        folder = self.branch(segment)

        pass

    def leaves(self):
        files = self._folder.files(recursive=True)
        leaves = []
        for file in files:
            try:
                leaves.append(Leaf(file))
            except Exception as e:
                logger.warning(f'File is not leaf: {file}')
        return leaves

    def shape(self, leaf):
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
        if not kwargs:
            logger.debug('No input arguments. Skipping reshape.')
        else:
            self.add(kwargs)
            self.write()
            self.prune()

    def prune_leaf(self, leaf):
        if not leaf.folder() == self.branch(leaf):
            leaf = leaf.move(self.branch(leaf))
            logger.debug(f'Move leaf: {leaf}')
        return leaf

    def prune(self, delete_not_leaf=True):
        files = self.files()
        for file in files:
            try:
                leaf = Leaf(file)
                tmp = self.prune_leaf(leaf)
                _ = self.shape(tmp)
            except ValueError:
                if delete_not_leaf:
                    logger.warning(f'Delete file that is not leaf: {file}')
                    file.delete()

        folders = self.folders()
        levels_and_folders = [(len(x.parts()), x) for x in folders]
        levels_and_folders.sort(reverse=True)
        for _, folder in levels_and_folders:
            if folder.is_empty():
                folder.remove()

    def folders(self, pattern='*', recursive=True):
        paths = self._folder.folders(pattern=pattern, recursive=recursive)
        return [Folder(x) for x in paths]

    def files(self, pattern='*', recursive=True):
        paths = self._folder.files(pattern=pattern, recursive=recursive)
        return [File(x) for x in paths]

    def weeds(self):
        leaves = self.leaves()
        files = self.files()
        not_leaves = len(files) - len(leaves)
        compression_mismatch = 0
        encryption_mismatch = 0
        for leaf in leaves:
            if leaf.is_compressed() != self.compress_all:
                compression_mismatch += 1
            if leaf.is_encrypted() != self.encrypt_all:
                encryption_mismatch += 1
        folders = self.folders()
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
        weeds = self.weeds()
        return weeds['total_weeds']


class TreeError(Exception):
    pass
