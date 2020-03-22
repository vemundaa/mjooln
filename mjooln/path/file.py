import gzip
import logging
import os
import shutil
import hashlib

from mjooln.core.crypt import Crypt
from mjooln.core.dic_doc import Doc
from mjooln.path.path import Path
from mjooln.path.folder import Folder

logger = logging.getLogger(__name__)


class File(Path):

    JSON_EXTENSION = 'json'
    COMPRESSED_EXTENSION = 'gz'
    CRYPT_EXTENSION = 'aes'

    RESERVED_EXTENSIONS = [COMPRESSED_EXTENSION, CRYPT_EXTENSION]

    HIDDEN_STARTSWITH = '.'
    EXTENSION_SEPARATOR = '.'

    _salt = b'O89ogfFYLGUts3BM1dat4vcQ'

    _hidden = None
    _compressed = None
    _encrypted = None
    # TODO: Reconsider if json handling should be in file.
    _json = None
    # TODO: Add binary flag based on extension (all other than text is binary..)
    # TODO: Facilitate child classes with custom read/write needs

    @classmethod
    def join(cls, *args):
        # Purely cosmetic for IDE
        return super().join(*args)

    @classmethod
    def home(cls, file_name):
        return cls.join(Folder.home(), file_name)

    @classmethod
    def crypt_key_from_crypt_key_or_password(cls, crypt_key=None, password=None):
        """Using a password will make a encryption_key combined with the internal class salt"""
        if crypt_key and password:
            raise FileError('Use either crypt_key or password.')
        elif not crypt_key and not password:
            raise FileError('crypt_key or password missing')
        if crypt_key:
            return crypt_key
        else:
            return Crypt.key_from_password(cls._salt, password)

    def __new__(cls, path_str, is_binary=False, *args, **kwargs):
        # TODO: Raise exception if reserved extensions are used inappropriately
        instance = Path.__new__(cls, path_str)
        if instance.exists():
            if instance.is_volume():
                raise FileError(f'Path is volume, not file: {path_str}')
            elif instance.is_folder():
                raise FileError(f'Path is existing folder, not file: {path_str}')
        instance._hidden = instance.name().startswith(cls.HIDDEN_STARTSWITH)
        instance._compressed = cls.COMPRESSED_EXTENSION in instance.extensions()
        instance._encrypted = cls.CRYPT_EXTENSION in instance.extensions()
        instance._json = cls.JSON_EXTENSION in instance.extensions()
        return instance

    def parts(self):
        parts = self.name().split(self.EXTENSION_SEPARATOR)
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

    def write(self, data, mode='w',
              crypt_key=None, password=None,
              human_readable=True, **kwargs):
        # TODO: Require compression if file is encrypted?
        if self._encrypted:
            crypt_key = self.crypt_key_from_crypt_key_or_password(crypt_key, password)
        elif crypt_key or password:
            raise FileError(f'File does not have crypt extension '
                            f'({self.CRYPT_EXTENSION}), but a crypt_key '
                            f'or password was sent as input to write.')
        if self._json:
            data = Doc.dic_to_doc(data, human_readable=human_readable)

        self.folder().touch()
        if self._compressed:
            self._write_compressed(data)
            if self._encrypted:
                if self.size() > 100000:
                    logger.warning('On the fly encrypt/compress not implemented. '
                                   'There is an extra read/write from/to disk. '
                                   'In other words, this is a hack.')
                # TODO: Refactor to write once, but verify zlib/gzip compatibility
                data = self._read(mode='rb')
                data = Crypt.encrypt(data, crypt_key)
                self.delete()
                self._write(data, mode='wb')
        else:
            if self._encrypted:
                if not isinstance(data, bytes):
                    data = data.encode()
                data = Crypt.encrypt(data, crypt_key)
                self._write(data, mode='wb')
            else:
                self._write(data, mode=mode)

    def _write(self, data, mode='w'):
        with open(self, mode=mode) as f:
            f.write(data)

    def _write_compressed(self, content):
        if not isinstance(content, bytes):
            content = content.encode()
        with gzip.open(self, mode='wb') as f:
            f.write(content)

    def read(self, mode='r', crypt_key=None, password=None, *args, **kwargs):
        if not self.exists():
            raise FileError(f'Cannot read from file that does not exist: {self}')
        if self._encrypted:
            crypt_key = self.crypt_key_from_crypt_key_or_password(crypt_key, password)
        elif crypt_key or password:
            raise FileError(f'File does not have crypt extension '
                            f'({self.CRYPT_EXTENSION}), but a crypt_key '
                            f'or password was sent as input to write.')
        if self._compressed:
            if self._encrypted:
                logger.warning('On the fly encrypt/compress not implemented. '
                               'There is an extra read/write from/to disk. '
                               'In other words, this is a hack.')
                # TODO: Refactor to read once, but verify zlib/gzip compatibility
                decrypted_file = self.decrypt(crypt_key, delete_original=False)
                data = decrypted_file._read_compressed(mode=mode)
                decrypted_file.delete()
            else:
                data = self._read_compressed(mode=mode)
        else:
            if self._encrypted:
                data = self._read(mode='rb')
                data = Crypt.decrypt(data, crypt_key)
                if 'b' not in mode:
                    data = data.decode()
            else:
                data = self._read(mode=mode)

        if self._json:
            data = Doc.doc_to_dic(data)
        return data

    def _read(self, mode='r'):
        with open(self, mode=mode) as f:
            content = f.read()
        return content

    def _read_compressed(self, mode='rb'):
        with gzip.open(self, mode=mode) as f:
            content = f.read()
        if 'b' not in mode:
            if not isinstance(content, str):
                content = content.decode()
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

    def move(self, new_folder, new_name=None):
        new_folder.touch()
        if new_name:
            new_file = File.join(new_folder, new_name)
        else:
            new_file = File.join(new_folder, self.name())
        if self.volume() == new_folder.volume():
            os.rename(self, new_file)
        else:
            shutil.move(self, new_file)
        return new_file

    def copy(self, new_folder, new_name=None):
        if self.folder() == new_folder:
            raise FileError(f'Cannot copy a file to the same folder: {new_folder}')
        new_folder.touch()
        if new_name:
            new_file = File.join(new_folder, new_name)
        else:
            new_file = File.join(new_folder, self.name())
        shutil.copyfile(self, new_file)
        return new_file

    def compress(self, delete_original=True):
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

    def encrypt(self, crypt_key, delete_original=True):
        if self._encrypted:
            raise FileError(f'File is already encrypted: {self}')
        logger.debug(f'Encrypt file: {self}')
        encrypted_file = File(self + '.' + self.CRYPT_EXTENSION)
        data = self._read(mode='rb')
        encrypted = Crypt.encrypt(data, crypt_key)
        encrypted_file._write(encrypted, mode='wb')
        if delete_original:
            self.delete()
        return encrypted_file

    def decrypt(self, crypt_key, delete_original=True):
        if not self._encrypted:
            raise FileError(f'File is not encrypted: {self}')

        logger.debug(f'Decrypt file: {self}')
        decrypted_file = File(self.replace('.' + self.CRYPT_EXTENSION, ''))
        data = self._read(mode='rb')
        decrypted = Crypt.decrypt(data, crypt_key)
        decrypted_file._write(decrypted, mode='wb')
        if delete_original:
            self.delete()
        return decrypted_file

    def glob(self, pattern='*', recursive=False):
        paths = super().glob(pattern=pattern, recursive=recursive)
        return (File(x) for x in paths if x.is_file())


class FileError(Exception):
    pass
