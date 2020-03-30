import logging
from mjooln.core.segment import Segment, SegmentError
from mjooln.core.crypt import CryptError
from mjooln.path.folder import Folder
from mjooln.path.file import File
from mjooln.root.root import Root
from mjooln.tree.leaf import Leaf, LeafError, NotALeafError

logger = logging.getLogger(__name__)


class Tree(Root):

    TREE = 'tree'
    SPECIES = TREE

    EXTENSION = None

    @classmethod
    def is_tree(cls, folder, species=SPECIES):
        is_root = Root.is_root(folder)
        if not is_root:
            return False
        else:
            root = Root(folder)
            return root._species == species

    @classmethod
    def plant(cls, ground, key,
              species=SPECIES,
              extension=EXTENSION,
              compress_all=False,
              encrypt_all=False,
              crypt_key=None,
              key_level=Segment.LEVEL_NONE,
              date_level=Segment.LEVEL_NONE,
              time_level=Segment.LEVEL_NONE,
              **kwargs):
        tree = super(Tree, cls).plant(ground, key,
                                      species=species,
                                      extension=extension,
                                      compress_all=compress_all,
                                      encrypt_all=encrypt_all,
                                      key_level=key_level,
                                      date_level=date_level,
                                      time_level=time_level,
                                      **kwargs)
        if crypt_key:
            return cls(ground.append(key), crypt_key=crypt_key)
        else:
            return tree

    def __init__(self, folder, default=False, crypt_key=None):
        self.extension = self.EXTENSION
        self.compress_all = False
        self.encrypt_all = False
        self.key_level = Segment.LEVEL_NONE
        self.date_level = Segment.LEVEL_NONE
        self.time_level = Segment.LEVEL_NONE
        super(Tree, self).__init__(folder, default=default)
        if self.encrypt_all and not crypt_key:
            raise TreeError('Tree is encrypt_all, and therefore needs an encryption key '
                            'as input to constructor. Look in Crypt on how to make this.')
        self._crypt_key = crypt_key

    def branch(self, segment):
        levels = segment.levels(key_level=self.key_level,
                                date_level=self.date_level,
                                time_level=self.time_level)
        return self._folder.append(levels)

    @classmethod
    def _leaf_name(cls, segment, extension, compressed, encrypted):
        new_names = [str(segment), extension]
        if compressed:
            new_names.append(File.COMPRESSED_EXTENSION)
        if encrypted:
            new_names.append(File.CRYPT_EXTENSION)
        new_name = File.EXTENSION_SEPARATOR.join(new_names)
        return new_name

    def grow(self, native_file, segment=None, delete_source=True, **kwargs):
        if not native_file.exists():
            raise TreeError(f'Cannot grow Leaf from non existent '
                            f'path: {native_file}')
        if not native_file.is_file():
            raise TreeError(f'Native is not a file: {native_file}')

        if self.extension and native_file.extension() != self.extension:
            raise TreeError(f'File has invalid extension: {native_file.extension()}. '
                            f'Should be: {self.extension}')
        elif not self.extension:
            extension = native_file.extension()
        else:
            extension = self.extension

        if not segment:
            try:
                segment = Segment(native_file.stub())
            except SegmentError as se:
                raise TreeError(f'File name is not a valid segment: {native_file.name()}. '
                                f'Add segment as parameter to override file name.') from se

        new_name = self._leaf_name(segment,
                                   extension=extension,
                                   compressed=native_file.is_compressed(),
                                   encrypted=native_file.is_encrypted())

        folder = self.branch(segment)
        if delete_source:
            file = native_file.move(folder, new_name)
        else:
            file = native_file.copy(folder, new_name)
        leaf = Leaf(file)
        logger.debug(f'Added leaf: {leaf}')
        self._shape(leaf)
        return leaf

    def leaves(self):
        for path in self.files():
            try:
                yield Leaf(path)
            except NotALeafError:
                logger.warning(f'File is not leaf: {path}')

    def _shape(self, leaf):
        leaf.shape(compress=self.compress_all,
                   encrypt=self.encrypt_all,
                   crypt_key=self._crypt_key)

    def shape(self):
        for leaf in self.leaves():
            self._shape(leaf)

    def _reshape(self, **kwargs):
        if not kwargs:
            logger.debug('No input arguments. Skipping reshape.')
            return False
        else:
            self.add(kwargs)
            self.write()
            return True

    def reshape(self, **kwargs):
        if self._reshape(**kwargs):
            logger.debug('Reshape tree')
            self.prune()
            self.shape()

    def _prune(self, leaf):
        leaf.prune(self.branch(leaf.segment()))

    def prune(self, delete_not_leaf=True, delete_empty_folders=True):
        files = self.files()
        for file in files:
            try:
                leaf = Leaf(file)
                self._prune(leaf)
            except NotALeafError:
                if delete_not_leaf:
                    logger.warning(f'Deleting file that is not leaf: {file}')
                    file.delete()

        if delete_empty_folders:
            folders = self.folders()
            levels_and_folders = [(len(x.parts()), x) for x in folders]
            levels_and_folders.sort(reverse=True)
            for _, folder in levels_and_folders:
                if folder.is_empty():
                    folder.remove()

    def folders(self, pattern='*', recursive=True):
        paths = self._folder.glob(pattern=pattern, recursive=recursive)
        return (Folder(x) for x in paths if x.is_folder())

    def files(self, pattern='*', recursive=True):
        paths = self._folder.glob(pattern=pattern, recursive=recursive)
        return (File(x) for x in paths if x.is_file())

    def weeds(self):
        leaves = list(self.leaves())
        files = list(self.files())
        not_leaves = len(files) - len(leaves)
        compression_mismatch = 0
        encryption_mismatch = 0
        for leaf in leaves:
            if leaf.file().is_compressed() != self.compress_all:
                compression_mismatch += 1
            if leaf.file().is_encrypted() != self.encrypt_all:
                encryption_mismatch += 1
        folders = self.folders()
        empty_folders = sum([x.is_empty() for x in folders])
        return {
            'not_leaves': not_leaves,
            'compression_mismatch': compression_mismatch,
            'encryption_mismatch': encryption_mismatch,
            'empty_folders': empty_folders,
            'total_weeds': not_leaves + compression_mismatch + encryption_mismatch + empty_folders
        }

    def total_weeds(self):
        weeds = self.weeds()
        return weeds['total_weeds']


class TreeError(Exception):
    pass
