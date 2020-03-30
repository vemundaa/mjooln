import pandas as pd
from mjooln.tree.leaf import Leaf, NotALeafError


class NotABirchLeaf(Exception):
    pass


class BirchLeafError(Exception):
    pass


class BirchLeaf(Leaf):

    EXTENSION = 'csv'

    @classmethod
    def grow(cls, file, df, **kwargs):
        if file.is_encrypted():
            raise BirchLeafError(f'Encryption not implemented')
        if file.exists():
            raise BirchLeafError(f'File already exists. Nothing grows here: {file}')
        df.to_csv(str(file), **kwargs)
        return cls(file)

    def __init__(self, file, **kwargs):
        try:
            super(BirchLeaf, self).__init__(file, **kwargs)
        except NotALeafError as nl:
            raise NotABirchLeaf(nl)

    def feel(self, crypt_key=None, **kwargs):
        if self._file.is_encrypted():
            # TODO: Improve this hack to avoid creating temporary file
            tmp_file = self._file.decrypt(crypt_key=crypt_key, delete_original=False)
            data = pd.read_csv(str(tmp_file), **kwargs)
            tmp_file.delete()
        else:
            data = pd.read_csv(str(self._file), **kwargs)

        return data
