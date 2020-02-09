import os
import glob
import logging
import socket
from mjooln.core.zulu import Zulu
import psutil
from sys import platform

logger = logging.getLogger(__name__)


class Path(str):

    LINUX = 'linux'
    WINDOWS = 'windows'
    OSX = 'osx'
    PLATFORM = {
        'linux': LINUX,
        'linux2': LINUX,
        'darwin': OSX,
        'win32': WINDOWS,
    }

    @classmethod
    def home(cls):
        return cls(os.path.expanduser('~'))

    @classmethod
    def current(cls):
        return cls(os.getcwd())

    @classmethod
    def join(cls, *args):
        return cls(os.path.join(*args))

    @classmethod
    def mountpoints(cls):
        return [x.mountpoint for x in psutil.disk_partitions(all=True)]

    @classmethod
    def has_valid_mountpoint(cls, path_str):
        return len([x for x in cls.mountpoints() if path_str.startswith(x)]) > 0

    @classmethod
    # TODO: Rename?
    def platform(cls):
        if platform in cls.PLATFORM:
            return cls.PLATFORM[platform]
        else:
            raise PathError(f'Unknown platform {platform}. '
                            f'Known platforms are: {cls.PLATFORM.keys()}')

    @classmethod
    def host(cls):
        return socket.gethostname()

    @classmethod
    def elf(cls, path, **kwargs):
        if isinstance(path, cls):
            return path
        else:
            return cls(path)

    def __new__(cls, path_str, **kwargs):
        # TODO: Remove? Since inherits string, it should not matter.
        if not isinstance(path_str, str):
            raise PathError(f'Input to constructor must be string, '
                            f'use elf() method for a softer approach.')
        if not os.path.isabs(path_str):
            path_str = path_str.replace('\\', '/')
            path_str = os.path.abspath(path_str)
        path_str = path_str.replace('\\', '/')
        # TODO: Add check on valid names
        instance = super(Path, cls).__new__(cls, path_str)
        if instance.platform() != cls.WINDOWS and ':' in path_str:
            raise PathError(f'Cannot have colon in path on this platform: {path_str}')
        if not cls.has_valid_mountpoint(path_str):
            raise PathError(f'Path does not have valid mountpoint for this platform: {path_str}')
        return instance

    def volume(self):
        mountpoints = self.mountpoints()
        candidates = [x for x in mountpoints if self.startswith(x)]
        if len(candidates) > 1:
            candidates = [x for x in candidates if not x == '/']
        if len(candidates) == 1:
            return Volume(candidates[0])
        else:
            raise PathError(f'Could not determine volume: {mountpoints}')

    def exists(self):
        return os.path.exists(self)

    def raise_if_not_exists(self):
        if not self.exists():
            raise PathError(f'Path does not exist: {self}')

    def is_volume(self):
        return self in self.mountpoints()

    def is_folder(self):
        if self.exists():
            return os.path.isdir(self)
        else:
            raise PathError(f'Cannot see if non existent path is a folder or not: {self}')

    def is_file(self):
        if self.exists():
            return os.path.isfile(self)
        else:
            raise PathError(f'Cannot see if non existent path is a file or not: {self}')

    def size(self):
        return os.stat(self).st_size

    def created(self):
        return Zulu.fromtimestamp(os.stat(self).st_ctime)

    def modified(self):
        return Zulu.fromtimestamp(os.stat(self).st_mtime)

    def parts(self):
        parts = str(self).split('/')
        if parts[0] == '':
            return parts[1:]
        else:
            return parts

    def glob(self, pattern='*', recursive=False):
        if self.is_folder():
            if recursive:
                paths = glob.glob(os.path.join(self, '**', pattern), recursive=recursive)
            else:
                paths = glob.glob(os.path.join(self, pattern))
            return (Path(x) for x in paths)
        else:
            raise PathError(f'Cannot glob/list a file: {self}')

    def list(self, pattern='*', recursive=False):
        return list(self.glob(pattern=pattern, recursive=recursive))


class Volume(Path):
    # TODO: Remove Volume class?

    @classmethod
    def elf(cls, path, **kwargs):
        if isinstance(path, Volume):
            return path
        else:
            return cls(path)

    def __new__(cls, path_str):
        # TODO: Add handling of network drive. Check if exists instead.
        instance = super(Volume, cls).__new__(cls, path_str)
        if not instance.is_volume():
            raise VolumeError(f'Path \'{instance}\' is not a volume. '
                              f'Allowed volumes are: {cls.mountpoints()}')
        return instance


class VolumeError(Exception):
    pass


class PathError(Exception):
    pass
