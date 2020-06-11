import os
import glob
import logging
import socket
import psutil
from sys import platform

from mjooln.atom.zulu import Zulu

logger = logging.getLogger(__name__)


# TODO: Handle network drives (i.e. not mounted)?
class Path(str):
    """ Absolute paths as a string with convenience functions

    No relative paths are allowed. Paths not starting with a valid
    mountpoint will be based in current folder.

    All backslashes are replaced with forward slash.
    """

    _FOLDER_SEPARATOR = '/'
    _LINUX = 'linux'
    _WINDOWS = 'windows'
    _OSX = 'osx'
    _PLATFORM = {
        'linux': _LINUX,
        'linux2': _LINUX,
        'darwin': _OSX,
        'win32': _WINDOWS,
    }

    @classmethod
    def home(cls, *args, **kwargs):
        """ Get path to user home folder

        Wrapper for ``os.path.expanduser()``

        :return: Path to home folder
        :rtype: Path
        """
        return cls(os.path.expanduser('~'))

    @classmethod
    def current(cls):
        """ Get current folder path

        Wrapper for ``os.getcwd()``

        :return: Path to current folder
        :rtype: Path
        """
        return cls(os.getcwd())

    @classmethod
    def join(cls, *args):
        """ Join strings to path

        Wrapper for ``os.path.join()``

        Relative paths will include current folder::

            Path.current()
                '/Users/zaphod/dev'
            Path.join('code', 'earth')
                '/Users/zaphod/dev/code/donald'

        :return: Absolute path
        :rtype: Path
        """
        return cls(os.path.join(*args))

    @classmethod
    def mountpoints(cls):
        """ List valid mountpoints/partitions or drives

        Finds mountpoints/partitions on linux/osx, and drives (C:, D:) on
        windows.

        :return: Valid mountpoints or drives
        :rtype: list
        """
        return [x.mountpoint.replace('\\', cls._FOLDER_SEPARATOR)
                for x in psutil.disk_partitions(all=True)]

    @classmethod
    def has_valid_mountpoint(cls, path_str):
        """ Flags if the path starts with a valid mountpoint

        :return: True if path has valid mountpoint, False if not
        :rtype: bool
        """
        return len([x for x in cls.mountpoints()
                    if path_str.startswith(x)]) > 0

    @classmethod
    # TODO: Rename?
    def platform(cls):
        """ Get platform name

        :raises PathError: If platform is unknown
        :return: Platform name (linux/windows/osx)
        :rtype: str
        """
        if platform in cls._PLATFORM:
            return cls._PLATFORM[platform]
        else:
            raise PathError(f'Unknown platform {platform}. '
                            f'Known platforms are: {cls._PLATFORM.keys()}')

    @classmethod
    def host(cls):
        """ Get host name

        Wrapper for ``socket.gethostname()``

        :return: Host name
        :rtype: str
        """
        return socket.gethostname()

    @classmethod
    def elf(cls, path, **kwargs):
        if isinstance(path, cls):
            return path
        else:
            return cls(path)

    def __new__(cls, path_str, *args, **kwargs):
        # TODO: Remove? Since inherits string, it should not matter.
        # if not isinstance(path_str, str):
        #     raise PathError(f'Input to constructor must be string, '
        #                     f'use elf() method for a softer approach.')
        if not os.path.isabs(path_str):
            path_str = path_str.replace('\\', cls._FOLDER_SEPARATOR)
            path_str = os.path.abspath(path_str)
        path_str = path_str.replace('\\', cls._FOLDER_SEPARATOR)
        # TODO: Add check on valid names/characters
        instance = super(Path, cls).__new__(cls, path_str)
        if instance.platform() != cls._WINDOWS and ':' in path_str:
            raise PathError(f'Cannot have colon in path on this '
                            f'platform: {path_str}')
        if not cls.has_valid_mountpoint(path_str):
            raise PathError(f'Path does not have valid mountpoint '
                            f'for this platform: {path_str}')
        return instance

    def __fspath__(self):
        return str(self)

    def volume(self):
        """ Return path volume

        Volume is a collective term for mountpoint or drive

        :raises PathError: If volume cannot be determined
        :return: Volume of path
        :rtype: Path
        """
        mountpoints = self.mountpoints()
        candidates = [x for x in mountpoints if self.startswith(x)]
        if len(candidates) > 1:
            candidates = [x for x in candidates
                          if not x == self._FOLDER_SEPARATOR]
        if len(candidates) == 1:
            return Path(candidates[0])
        else:
            raise PathError(f'Could not determine volume: {mountpoints}')

    def exists(self):
        """ Check if path exists

        Wrapper for ``os.path.exists()``

        :return: True if path exists, False otherwise
        :rtype: bool
        """
        return os.path.exists(self)

    def raise_if_not_exists(self):
        """ Raises an exception if path does not exist

        :raises PathError: If path does not exist
        """
        if not self.exists():
            raise PathError(f'Path does not exist: {self}')

    def is_volume(self):
        """ Check if path is a volume

        :raises PathError: If path does not exist
        :return: True if path is a volume, False if not
        :rtype: bool
        """
        if self.exists():
            return self in self.mountpoints()
        else:
            raise PathError(f'Cannot see if non existent path '
                            f'is a volume or not: {self}')

    def is_folder(self):
        """ Check if path is a folder

        :raises PathError: If path does not exist
        :return: True if path is a folder, False if not
        :rtype: bool
        """
        if self.exists():
            return os.path.isdir(self)
        else:
            raise PathError(f'Cannot see if non existent path '
                            f'is a folder or not: {self}')

    def is_file(self):
        """ Check if path is a file

        :raises PathError: If path does not exist
        :return: True if path is a file, False if not
        :rtype: bool
        """
        if self.exists():
            return os.path.isfile(self)
        else:
            raise PathError(f'Cannot see if non existent path '
                            f'is a file or not: {self}')

    def size(self):
        """ Return file or folder size

        .. warning:: If Path is a folder, ``size()`` will return a small number,
            representing the size of the folder object, not its contents.
            For finding actual disk usage of a folder, use
            :meth:`.Folder.disk_usage()` in the :class:`.Folder` class

        :raises PathError: If path does not exist
        :returns: File or folder size
        :rtype: int
        """
        if self.exists():
            return os.stat(self).st_size
        else:
            raise PathError(f'Cannot determine size of non existent path: {self}')

    def created(self):
        """ Get created timestamp

        :return: Timestamp created
        :rtype: Zulu
        """
        return Zulu.fromtimestamp(os.stat(self).st_ctime)

    def modified(self):
        """
        Get modified timestamp

        :returns: Timestamp modified
        :rtype: Zulu
        """
        return Zulu.fromtimestamp(os.stat(self).st_mtime)

    def parts(self):
        """ Get list of parts in path

        :returns: String parts of path
        :rtype: list
        """
        parts = str(self).split(self._FOLDER_SEPARATOR)
        if parts[0] == '':
            return parts[1:]
        else:
            return parts

    def glob(self, pattern='*', recursive=False):
        """ Generator for paths with the given pattern

        Wrapper for ``glob.glob``

        :raises PathError: If path does not exist, or if path is not a folder
            (cannot list a file)
        :param pattern: Search pattern
        :param recursive: Recursive flag (when True, all subfolders will be
            searched)
        :type recursive: bool
        :returns: Generator of paths in folder
        :rtype: generator
        """
        if self.exists():
            if self.is_folder():
                if recursive:
                    paths = glob.glob(os.path.join(self, '**', pattern),
                                      recursive=recursive)
                else:
                    paths = glob.glob(os.path.join(self, pattern))
                return (Path(x) for x in paths)
            else:
                raise PathError(f'Cannot glob/list a file: {self}')
        else:
            raise PathError(f'Cannot glob/list a non existent path: {self}')

    def list(self, pattern='*', recursive=False):
        """ List paths in folder

        :raises PathError: If path does not exist, or if path is not a folder
            (cannot list a file)
        :param pattern: Wildcard or pattern
        :param recursive: Recursive flag (when True, all subfolders will be
            searched)
        :return: list
        """
        return list(self.glob(pattern=pattern, recursive=recursive))

    def folders(self, pattern='*', recursive=False):
        """ List folders in folder

        :raises PathError: If path does not exist, or if path is not a folder
            (cannot list a file)
        :param pattern: Wildcard or pattern
        :param recursive: Recursive flag. When True, all subfolders will be
            searched
        :return: All folders in folder matching the pattern
        :rtype: list
        """
        paths = self.glob(pattern=pattern, recursive=recursive)
        return [Path(x) for x in paths if x.is_folder()]

    def files(self, pattern='*', recursive=False):
        """ List files in folder

        :raises PathError: If path does not exist, or if path is not a folder
            (cannot list a file)
        :param pattern: Wildcard or pattern
        :param recursive: Recursive flag. When True, all subfolders will be
            searched
        :return: All files in folder matching the pattern
        :rtype: list
        """
        paths = self.glob(pattern=pattern, recursive=recursive)
        return [Path(x) for x in paths if x.is_file()]

    @classmethod
    def dev_print_tree(cls, startpath):
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print('{}{}'.format(subindent, f))

class PathError(Exception):
    """ Convenience class for raising errors """
    pass
