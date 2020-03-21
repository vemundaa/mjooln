import logging
import os
import shutil

from mjooln.path.path import Path

logger = logging.getLogger(__name__)


class Folder(Path):

    @classmethod
    def join(cls, *args):
        # Purely cosmetic for IDE
        return super().join(*args)

    def __new__(cls, path_str, *args, **kwargs):
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

    def create(self, error_if_exists=True):
        """Create new folder, including non existent parent folders"""
        if not self.exists():
            os.makedirs(self)
            return True
        else:
            if error_if_exists:
                raise FolderError(f'Folder already exists: {self}')
            return False

    def touch(self):
        """Create folder if it does not exist, ignore otherwise"""
        self.create(error_if_exists=False)

    def untouch(self):
        """Remove folder if it exists, ignore otherwise"""
        self.remove(error_if_not_exists=False)

    def parent(self):
        return Folder(os.path.dirname(self))

    def append(self, *args):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, list):
                return Folder.join(self, '/'.join(arg))
            else:
                return Folder.join(self, arg)
        else:
            return Folder.join(self, *args)

    def is_empty(self):
        if self.exists():
            return len(list(self.list())) == 0
        else:
            raise FolderError(f'Cannot check if non existent folder is empty: {self}')

    def disk_usage(self):
        if self.exists():
            paths = self.glob(recursive=True)
            size = 0
            for path in paths:
                size += path.size()
            return size
        else:
            raise FolderError(f'Cannot determine disk usage of non existent folder: {self}')

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

    def remove(self, error_if_not_exists=True):
        if self.exists():
            os.rmdir(self)
        else:
            if error_if_not_exists:
                raise FolderError(f'Cannot remove a non existent folder: {self}')

    def name(self):
        return os.path.basename(self)


class FolderError(Exception):
    pass


if __name__ == '__main__':
    p = Folder.home()
    print(p)
    pp = Folder(p)
    print(pp)