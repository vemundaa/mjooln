import logging
from mjooln import Root, Segment, SegmentError, CryptError, Folder, File
from mjooln.tree.leaf import Leaf

logger = logging.getLogger(__name__)


class Tree(Root):

    TREE = 'tree'
    SPECIES = TREE

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
              compress_all=False,
              encrypt_all=False,
              encryption_key=None,
              key_levels=0,
              date_levels=0,
              time_levels=0,
              **kwargs):
        tree = super(Tree, cls).plant(ground, key,
                                      species=species,
                                      compress_all=compress_all,
                                      encrypt_all=encrypt_all,
                                      key_levels=key_levels,
                                      date_levels=date_levels,
                                      time_levels=time_levels,
                                      **kwargs)
        if encryption_key:
            return cls(ground.append(key), encryption_key=encryption_key)
        else:
            return tree

    def __init__(self, folder, default=False, encryption_key=None):
        self.compress_all = False
        self.encrypt_all = False
        self.key_levels = 0
        self.date_levels = 0
        self.time_levels = 0
        super(Tree, self).__init__(folder, default=default)
        if self.encrypt_all and not encryption_key:
            raise TreeError('Tree is encrypt_all, and therefore needs an encryption key '
                            'as input to constructor. Look in Crypt on how to make this.')
        self._encryption_key = encryption_key

    def branch(self, segment):
        levels = segment.levels(key_levels=self.key_levels,
                                date_levels=self.date_levels,
                                time_levels=self.time_levels)
        return self._folder.append(levels)

    def grow(self, native_file, segment=None, delete_source=True):
        if not native_file.exists():
            raise TreeError(f'Cannot grow Leaf from non existent '
                            f'path: {native_file}')
        if not native_file.is_file():
            raise TreeError(f'Native is not a file: {native_file}')

        if segment:
            new_name = native_file.name().replace(native_file.stub(), str(segment))
        else:
            new_name = None
            try:
                segment = Segment(native_file.stub())
            except SegmentError as se:
                raise TreeError(f'File name is not a valid segment: {native_file.name()}. '
                                f'Add segment as parameter to override file name.') from se
        folder = self.branch(segment)
        if delete_source:
            file = native_file.move(folder, new_name)
        else:
            file = native_file.copy(folder, new_name)
        leaf = Leaf(file)
        logger.debug(f'Added leaf: {leaf}')
        leaf = self.shape(leaf)
        return leaf

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
                            f'attempting reshape of {leaf}. Original error: {ce}')

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
            'total_weeds': not_leaves + compression_mismatch + encryption_mismatch + empty_folders
        }

    def total_weeds(self):
        weeds = self.weeds()
        return weeds['total_weeds']


class TreeError(Exception):
    pass
