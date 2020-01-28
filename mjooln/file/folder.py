import logging
import os
import shutil

from mjooln.file.path import Path

logger = logging.getLogger(__name__)


class Folder(Path):

    @classmethod
    def join(cls, *args):
        # Purely cosmetic for IDE
        return super().join(*args)

    @classmethod
    def elf(cls, folder):
        if isinstance(folder, Folder):
            return folder
        else:
            return super(Folder, cls).elf(folder)

    def __new__(cls, path_str):
        instance = super(Folder, cls).__new__(cls, path_str)
        # if cls.RESERVED in instance:
        #     raise FolderError(f'Folder path cannot contain \'{cls.RESERVED}\''
        #                       f'but was found here: {cls.RESERVED}')
        if instance.exists():
            if instance.is_volume():
                raise FolderError(f'Path is a volume, not a folder: {str(instance)}')
            elif instance.is_file():
                raise FolderError(f'Path is a file, not a folder: {str(instance)}')
        return instance

    def name(self):
        return os.path.basename(self)

    def create(self, error_if_exists=True):
        if not self.exists():
            os.makedirs(self)
            return True
        else:
            if error_if_exists:
                raise FolderError(f'Folder already exists: {self}')
            return False

    def touch(self):
        return self.create(error_if_exists=False)

    def parent(self):
        return Folder(os.path.dirname(self))

    def append(self, *args):
        return Folder.join(self, *args)

    def is_empty(self):
        if self.exists():
            return len(list(self.list())) == 0
        else:
            raise FolderError(f'Cannot check if non existent folder is empty: {self}')

    def empty(self):
        if self.exists():
            for name in os.listdir(self):
                path = os.path.join(self, name)
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        else:
            raise FolderError(f'Cannot empty a non existent folder: {self}')

    def remove(self):
        if self.exists():
            os.rmdir(self)
        else:
            raise FolderError(f'Cannot remove a non existent folder: {self}')

    def folders(self):
        paths = self.list()
        return [Folder(x) for x in paths if x.is_folder()]


class FolderError(Exception):
    pass
