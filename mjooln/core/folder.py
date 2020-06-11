import logging
import os
import shutil

from mjooln.core.path import Path

logger = logging.getLogger(__name__)


# TODO: Allow volume as folder
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
            if instance.is_file():
                raise FolderError(f'Path is a file, '
                                  f'not a folder: {str(instance)}')
        return instance

    def create(self, error_if_exists=True):
        """ Create new folder, including non existent parent folders

        :raises FolderError: If folder already exists, *and* ``error_if_exists``
            is set to ``True``
        :param error_if_exists: Error flag. If True, method will raise an
            error if the folder already exists
        :type error_if_exists: bool
        :returns: True if it was created, False if not
        :rtype: bool
        """
        if not self.exists():
            os.makedirs(self)
            return True
        else:
            if error_if_exists:
                raise FolderError(f'Folder already exists: {self}')
            return False

    def touch(self):
        """ Create folder if it does not exist, ignore otherwise

        :return: True if folder was created, False if not
        :rtype: bool
        """
        self.create(error_if_exists=False)

    def untouch(self):
        """ Remove folder if it exists, ignore otherwise
        :return: True if folder was removed, False otherwise
        :rtype: bool
        """
        self.remove(error_if_not_exists=False)

    def parent(self):
        """ Get parent folder

        :return: Parent folder
        :rtype: Folder
        """
        return Folder(os.path.dirname(self))

    def append(self, *args):
        """ Append strings or list of strings to current folder

        Example::

            f = Folder.current()
            print(f)
                '/Users/zaphod'

            f.append('dev', 'code', 'donald')
                '/Users/zaphod/dev/code/donald'

            parts = ['dev', 'code', 'donald']
            f.append(parts)
                '/Users/zaphod/dev/code/donald'

        :param args: Strings or list of strings
        :return: Appended folder as separate object
        :rtype: Folder
        """
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, list):
                return Folder.join(self, '/'.join(arg))
            else:
                return Folder.join(self, arg)
        else:
            return Folder.join(self, *args)

    def is_empty(self):
        """ Check if folder is empty

        :raise FolderError: If folder does not exist
        :return: True if empty, False if not
        :rtype: bool
        """
        if self.exists():
            return len(list(self.list())) == 0
        else:
            raise FolderError(f'Cannot check if non existent folder '
                              f'is empty: {self}')

    def disk_usage(self):
        """  Recursively determines disk usage of all contents in folder

        :raise FolderError: If folder does not exist
        :return: Disk usage of folder and subfolders
        :rtype: int
        """
        if self.exists():
            paths = self.glob(recursive=True)
            size = 0
            for path in paths:
                size += path.size()
            return size
        else:
            raise FolderError(f'Cannot determine disk usage of '
                              f'non existent folder: {self}')

    def empty(self):
        """  Recursively deletes all files and subfolders

        .. warning:: Be careful using this, as there is no double check
            before all contents is deleted. Recursively

        :raise FolderError: If folder does not exist
        :return: Disk usage of folder and subfolders
        :rtype: int
        """
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
        """ Remove folder

        Will raise an error if not empty

        :raises FolderError: If folder already exists, *and* ``error_if_exists``
            is set to ``True``
        :param error_if_exists: Error flag. If True, method will raise an
            error if the folder already exists
        :type error_if_exists: bool
        """
        if self.exists():
            os.rmdir(self)
        else:
            if error_if_not_exists:
                raise FolderError(f'Cannot remove a non existent '
                                  f'folder: {self}')

    def name(self):
        """ Get name of folder

        Example::

            f = Folder.current()
            f
                '/Users/zaphod'
            f.name()
                'donald'

            f = f.join('dev', 'code', 'donald')
            f
                '/Users/zaphod/dev/code/donald'
            f.name()
                'donald'

        :return: Name of folder
        :rtype: str
        """
        return os.path.basename(self)


class FolderError(Exception):
    pass
