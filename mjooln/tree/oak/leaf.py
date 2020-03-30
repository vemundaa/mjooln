import pandas as pd

from mjooln.core.segment import Segment
from mjooln.tree.leaf import Leaf, NotALeafError


class NotAnOakLeaf(Exception):
    pass


class OakLeafError(Exception):
    pass


class OakLeaf(Leaf):

    EXTENSION = 'h5'

    @classmethod
    def grow(cls, file, df, **kwargs):
        if file.is_encrypted():
            raise OakLeafError(f'Encryption not implemented for hdf5 files.')
        # if file.exists():
        #     raise OakLeafError(f'File already exists. Nothing grows here: {file}')
        segment = Segment(file.stub())
        df.to_hdf(str(file), segment.key, **kwargs)
        return cls(file)

    def __init__(self, file, **kwargs):
        try:
            super(OakLeaf, self).__init__(file, **kwargs)
        except NotALeafError as nl:
            raise NotAnOakLeaf(nl)

    def feel(self, crypt_key=None, **kwargs):
        if crypt_key:
            raise OakLeafError(f'Encryption not implemented for hdf5 files. '
                               f'Set crypt_key to None.')

        data = pd.read_hdf(str(self._file), key=self._segment.key, **kwargs)
        return data
