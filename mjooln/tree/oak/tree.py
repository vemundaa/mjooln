from mjooln.tree.tree import Tree
from mjooln.core.segment import Segment
from mjooln.path.file import File
from mjooln.tree.oak.leaf import OakLeaf, NotAnOakLeaf

from mjooln.core.zulu import Zulu


class OakError(Exception):
    pass


class Oak(Tree):

    OAK = 'oak'
    SPECIES = OAK

    @classmethod
    def plant(cls, ground, key,
              species=SPECIES,
              compress_all=False,
              encrypt_all=False,
              crypt_key=None,
              key_level=Segment.LEVEL_NONE,
              date_level=Segment.LEVEL_NONE,
              time_level=Segment.LEVEL_NONE,
              extension=OakLeaf.EXTENSION,
              allow_append=True,
              **kwargs):
        tree = super(Tree, cls).plant(ground, key,
                                      species=species,
                                      compress_all=compress_all,
                                      encrypt_all=encrypt_all,
                                      key_level=key_level,
                                      date_level=date_level,
                                      time_level=time_level,
                                      extension=extension,
                                      allow_append=allow_append,
                                      **kwargs)
        if crypt_key:
            return cls(ground.append(key), crypt_key=crypt_key)
        else:
            return tree

    def __init__(self, folder, default=False, crypt_key=None):
        if crypt_key:
            raise OakError('Encryption not implemented for hdf5 files. '
                           'Set crypt_key to None.')
        self.allow_append = True
        super(Oak, self).__init__(folder, default=default, crypt_key=crypt_key)

    def feed(self, key, df, zulu=None, identity=None, **kwargs):
        if not zulu:
            zulu = Zulu.elf(df.index.min())
        segment = Segment(key=key, zulu=zulu, identity=identity)
        leaf_name = self._leaf_name(segment=segment,
                                    extension=self.extension,
                                    compressed=self.compress_all,
                                    encrypted=self.encrypt_all)
        file = File.join(self.branch(segment), leaf_name)
        return OakLeaf.grow(file=file, df=df, **kwargs)

    def leaves(self):
        for path in self.files():
            try:
                yield OakLeaf(path)
            except NotAnOakLeaf:
                pass

    # def _sprout(self, segment):
    #     file_elements = [str(segment)]
    #     file_elements.append(self.file_type)
    #     if self.compress_all:
    #         file_elements.append(Sprout.COMPRESSED_EXTENSION)
    #     if self.encrypt_all:
    #         file_elements.append(Sprout.CRYPT_EXTENSION)
    #     file_name = Sprout.EXTENSION_SEPARATOR.join(file_elements)
    #     folder = self.branch(segment)
    #     return Sprout.join(folder, file_name)
    #
    # def feed(self, tree, feeder, **kwargs):
    #     leaves = tree.leaves()
    #     for leaf in leaves:
    #         df, segment = feeder.feed(leaf)
    #         sprout = self._sprout(segment)
    #         print(f'Grow: {sprout}')
    #         sprout.grow(df)




