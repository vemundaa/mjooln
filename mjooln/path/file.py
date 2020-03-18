import gzip
import logging
import os
import shutil
import hashlib

from mjooln.path.path import Path
from mjooln.path.folder import Folder

logger = logging.getLogger(__name__)

# TODO: Read from gz and encrypted directly


class File(Path):

    COMPRESSED_EXTENSION = 'gz'
    ENCRYPTED_EXTENSION = 'aes'
    RESERVED_EXTENSIONS = [COMPRESSED_EXTENSION, ENCRYPTED_EXTENSION]

    _hidden = None
    _compressed = None
    _binary = None

    @classmethod
    def join(cls, *args):
        # Purely cosmetic for IDE
        return super().join(*args)

    def __new__(cls, path_str, is_binary=False, *args, **kwargs):
        # TODO: Raise exception if reserved extensions are used inappropriately
        instance = Path.__new__(cls, path_str)
        if instance.exists():
            if instance.is_volume():
                raise FileError(f'Path is volume, not file: {path_str}')
            elif instance.is_folder():
                raise FileError(f'Path is existing folder, not file: {path_str}')
        instance._hidden = instance.name().startswith('.')
        instance._compressed = cls.COMPRESSED_EXTENSION in instance.extensions()
        instance._encrypted = cls.ENCRYPTED_EXTENSION in instance.extensions()
        return instance

    def parts(self):
        parts = self.name().split('.')
        if self.is_hidden():
            parts = parts[1:]
        return parts

    def extensions(self):
        return self.parts()[1:]

    def is_hidden(self):
        return self._hidden

    def is_encrypted(self):
        return self._encrypted

    def is_compressed(self):
        return self._compressed

    def stub(self):
        return self.parts()[0]

    def extension(self):
        extensions = self.extensions()
        extensions = [x for x in extensions if x not in self.RESERVED_EXTENSIONS]
        if len(extensions) == 1:
            return extensions[0]
        elif len(extensions) == 0:
            return None
        else:
            # TODO: Move this check to instantiation
            raise FileError(f'File has more than one '
                            f'not reserved ({self.RESERVED_EXTENSIONS}) '
                            f'extensions ({extensions}). '
                            f'Cannot determine a single extension: {self}')

    def md5_checksum(self):
        if not self.exists():
            raise FileError(f'Cannot make checksum if file does not exist: {self}')
        md5 = hashlib.md5()
        with open(self, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def delete(self, missing_ok=False):
        if self.exists():
            logger.debug(f'Delete file: {self}')
            os.unlink(self)
        elif not missing_ok:
            raise FileError(f'Tried to delete file that doesn\'t exist: {self}')

    def name(self):
        return os.path.basename(self)

    def write(self, content, mode='w', **kwargs):
        self.folder().touch()
        if self._compressed:
            self._write_compressed(content, mode=mode)
        else:
            self._write(content, mode=mode)

    def _write(self, content, mode='w'):
        with open(self, mode=mode) as f:
            f.write(content)

    def _write_compressed(self, content, mode='wb'):
        if not isinstance(content, bytes):
            content = content.encode()
        with gzip.open(self, mode=mode) as f:
            f.write(content)

    def read(self, *args, **kwargs):
        if self._compressed:
            return self._read_compressed()
        else:
            return self._read()

    def _read(self, mode='r'):
        with open(self, mode=mode) as f:
            content = f.read()
        return content

    def _read_compressed(self):
        with gzip.open(self, mode='rb') as f:
            content = f.read()
        return content

    def rename(self, new_name):
        new_path = self.join(self.folder(), new_name)
        os.rename(self, new_path)
        return File(new_path)

    def folder(self):
        return Folder(os.path.dirname(self))

    def files(self, pattern='*', recursive=False):
        files = self.folder().files(pattern='*', recursive=False)
        return [File(x) for x in files]

    def move(self, new_folder):
        new_folder.touch()
        new_file = File.join(new_folder, self.name())
        if self.volume() == new_folder.volume():
            os.rename(self, new_file)
        else:
            shutil.move(self, new_file)
        return new_file

    def copy(self, new_folder):
        if self.folder() == new_folder:
            raise FileError(f'Cannot copy a file to the same folder: {new_folder}')
        new_folder.touch()
        new_file = File.join(new_folder, self.name())
        shutil.copyfile(self, new_file)
        return new_file

    def compress(self, delete_original=True):
        if not self.exists():
            raise FileError(f'Cannot compress non existent file: {self}')
        if self.is_compressed():
            raise FileError(f'File already compressed: {self}')
        if self.is_encrypted():
            raise FileError(f'Cannot compress encrypted file: {self}. '
                            f'Decrypt file first')

        logger.debug(f'Compress file: {self}')
        old_size = self.size()
        new_file = File(self + '.' + self.COMPRESSED_EXTENSION)
        if new_file.exists():
            logger.warning(f'Overwrite existing gz-file: {new_file}')
        with open(self, 'rb') as f_in:
            with gzip.open(str(new_file), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        if delete_original:
            self.delete()
        new_file.compression_percent = 100 * (old_size - new_file.size()) / old_size
        logger.debug(f'Compressed with compression {new_file.compression_percent:.2f}')
        return new_file

    def decompress(self, delete_original=True, replace_if_exists=True):
        if not self.exists():
            raise FileError(f'Cannot decompress non existent file: {self}')
        if not self.is_compressed():
            raise FileError(f'File is not compressed: {self}')
        if self.is_encrypted():
            raise FileError(f'Cannot decompress encrypted file: {self}. '
                            f'Decrypt file first.')
        logger.debug(f'Decompress file: {self}')
        new_file = File(str(self).replace('.' + self.COMPRESSED_EXTENSION, ''))
        if new_file.exists():
            if replace_if_exists:
                logger.debug('Overwrite existing file: {}'.format(new_file))
            else:
                raise FileError(f'File already exists: \'{new_file}\'. '
                                f'Use replace_if_exists=True to ignore.')
        with gzip.open(self, 'rb') as f_in:
            with open(new_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        if delete_original:
            self.delete()
        new_file = File(new_file)
        new_file.compression_percent = None
        return new_file

    def glob(self, pattern='*', recursive=False):
        paths = super().glob(pattern=pattern, recursive=recursive)
        return (File(x) for x in paths if x.is_file())


class FileError(Exception):
    pass
