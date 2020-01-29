import gzip
import logging
import os
import shutil
import random
import string
import hashlib

from mjooln.core.crypt import AES
from mjooln.file.path import Path
from mjooln.file.folder import Folder

logger = logging.getLogger(__name__)

# TODO: Read from gz and encrypted directly


class File(Path):

    COMPRESSED_EXTENSION = 'gz'
    ENCRYPTED_EXTENSION = 'aes'
    RESERVED_EXTENSIONS = [COMPRESSED_EXTENSION, ENCRYPTED_EXTENSION]

    compression_percent = None

    @classmethod
    def join(cls, *args):
        # Purely cosmetic for IDE
        return super().join(*args)

    @classmethod
    def elf(cls, file,
            should_be_compressed=None,
            should_be_encrypted=None,
            key=None):
        file = super().elf(file)
        return file.elfer(should_be_compressed=should_be_compressed,
                          should_be_encrypted=should_be_encrypted,
                          key=key)

    def __new__(cls, path_str):
        instance = Path.__new__(cls, path_str)
        if instance.exists():
            if instance.is_volume():
                raise FileError(f'Path is volume, not file: {path_str}')
            elif instance.is_folder():
                raise FileError(f'Path is existing folder, not file: {path_str}')
        return instance

    def is_hidden(self):
        return self.name().startswith('.')

    def parts(self):
        parts = self.name().split('.')
        if self.is_hidden():
            parts = parts[1:]
        return parts

    def extensions(self):
        return self.parts()[1:]

    def is_encrypted(self):
        return self.ENCRYPTED_EXTENSION in self.extensions()

    def is_compressed(self):
        return self.COMPRESSED_EXTENSION in self.extensions()

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
            raise FileError(f'File has more than one '
                            f'not reserved ({self.RESERVED_EXTENSIONS}) '
                            f'extension ({extensions}): {self}')

    def write(self, content, mode='w'):
        folder = self.folder()
        folder.touch()
        with open(self, mode=mode) as f:
            f.write(content)

    def read(self, mode='r'):
        with open(self, mode=mode) as f:
            content = f.read()
        return content

    def md5_checksum(self):
        if not self.exists():
            raise FileError(f'Cannot make checksum if file does not exist: {self}')
        md5 = hashlib.md5()
        with open(self, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def elfer(self,
              should_be_compressed=None,
              should_be_encrypted=None,
              key=None):
        tmp = self
        if should_be_compressed is not None:
            if should_be_compressed:
                tmp = tmp.elf_compress(key=key)
            else:
                tmp = tmp.elf_decompress(key=key)
        if should_be_encrypted is not None:
            if should_be_encrypted:
                tmp = tmp.elf_encrypt(key=key)
            else:
                tmp = tmp.elf_decrypt(key=key)
        return tmp

    def elf_encrypt(self, key):
        if self.is_encrypted():
            return self
        else:
            return self.encrypt(key)

    def elf_decrypt(self, key):
        if not self.is_encrypted():
            return self
        else:
            return self.decrypt(key)

    def elf_compress(self, key=None):
        if self.is_compressed():
            return self
        else:
            if self.is_encrypted():
                if not key:
                    raise FileError(f'Need to decrypt/encrypt in order to compress file. '
                                    f'Cannot do that without a key.')
                tmp = self.decrypt(key)
                tmp = tmp.compress()
                return tmp.encrypt(key)
            else:
                return self.compress()

    def elf_decompress(self, key=None):
        if not self.is_compressed():
            return self
        else:
            if self.is_encrypted():
                if not key:
                    raise FileError(f'Need to decrypt/encrypt in order to decompress file. '
                                    f'Cannot do that without a key.')
                tmp = self.decrypt(key)
                tmp = tmp.decompress()
                return tmp.encrypt(key)

            return self.compress()

    def encrypt(self, key, delete_original=True):
        if not self.exists():
            raise FileError(f'Cannot encrypt non existent file: {self}')
        if self.is_encrypted():
            raise FileError(f'File is already encrypted: {self}')
        logger.debug(f'Encrypt file: {self}')
        encrypted_file = File(self + '.' + self.ENCRYPTED_EXTENSION)
        data = self.read(mode='rb')
        encrypted = AES.encrypt(data, key)
        encrypted_file.write(encrypted, mode='wb')
        if delete_original:
            self.delete()
        return encrypted_file

    def decrypt(self, key, delete_original=True):
        if not self.exists():
            raise FileError(f'Cannot decrypt non existent file: {self}')
        if not self.is_encrypted():
            raise FileError(f'File is already encrypted: {self}')

        logger.debug(f'Decrypt file: {self}')
        decrypted_file = File(self.replace('.' + self.ENCRYPTED_EXTENSION, ''))
        data = self.read(mode='rb')
        decrypted = AES.decrypt(data, key)
        decrypted_file.write(decrypted, mode='wb')
        if delete_original:
            self.delete()
        return decrypted_file

    def delete(self, missing_ok=False):
        if self.exists():
            logger.debug(f'Delete file: {self}')
            os.unlink(self)
        elif not missing_ok:
            raise FileError(f'Tried to delete file that doesn\'t exist: {self}')

    def name(self):
        return os.path.basename(self)

    def rename(self, new_name):
        new_path = self.join(self.folder(), new_name)
        os.rename(self, new_path)
        return File(new_path)

    def folder(self):
        return Folder(os.path.dirname(self))

    def files(self):
        paths = self.list()
        return [File(x) for x in paths if x.is_file()]

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
        return [File(x) for x in paths if x.is_file()]


class TextFile(File):

    def write(self, text, mode='wt'):
        super().write(content=text, mode='wt')

    def append(self, text, mode='at+'):
        super().write(content=text, mode=mode)

    def read(self, mode='rt'):
        return super().read(mode='rt')

    @classmethod
    def new(cls, path, text):
        file = TextFile.elf(path)
        if file.exists():
            raise FileError(f'File already exists: {file}')
        else:
            file.write(text=text)
            return file

    @classmethod
    def dev_create_sample(cls, path_str, num_chars=1000):
        text = ''.join(random.choices(string.ascii_uppercase + string.digits + '\n',
                                      k=num_chars))
        file = cls(path_str)
        if not file.exists():
            file.write(text)
        else:
            raise FileError(f'File already exists: {file}')
        return file


class FileError(Exception):
    pass
