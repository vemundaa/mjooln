import gzip
import logging
import os
import shutil
import hashlib

from mjooln.core.crypt import Crypt
from mjooln.core.dic_doc import Doc
from mjooln.core.path import Path
from mjooln.core.folder import Folder

logger = logging.getLogger(__name__)

# TODO: Add yaml files


class File(Path):
    """
    Convenience class for file handling

    Create and read a file::

        f = File('my_file.txt')
        f.write('Hello world')
        f.read()
            'Hello world'
        f.size()
            11

    Compress and encrypt::

        fc = f.compress()
        fc.name()
            'my_file.txt.gz'
        fc.read()
            'Hello world'

        crypt_key = Crypt.generate_key()
        crypt_key
            b'aLQYOIxZOLllYThEKoXTH_eqTQGEnXm9CUl2glq3a2M='
        fe = fc.encrypt(crypt_key)
        fe.name()
            'my_file.txt.gz.aes'
        fe.read(crypt_key=crypt_key)
            'Hello world'

    Create an encrypted file, and write to it::

        ff = File('my_special_file.txt.aes')
        ff.write('Hello there', password='123')
        ff.read(password='123')
            'Hello there'

        f = open(ff)
        f.read()
            'gAAAAABe0BYqPPYfzha3AKNyQCorg4TT8DcJ4XxtYhMs7ksx22GiVC03WcrMTnvJLjTLNYCz_N6OCmSVwk29Q9hoQ-UkN0Sbbg=='
        f.close()

    .. note:: Using the ``password`` parameter, builds an encryption key by
        combining it with the builtin (i.e. hard coded) class salt.
        For proper security, generate your
        own salt with :meth:`.Crypt.salt()`. Then use
        :meth:`.Crypt.key_from_password()` to generate a crypt_key

    .. warning:: \'123\' is not a real password

    """

    #: Files with this extension will convert from JSON to dict when reading
    #: the file, and dict to JSON when writing
    JSON_EXTENSION = 'json'

    #: Files with this extension will compress text before writing to file
    #: and decompress after reading
    COMPRESSED_EXTENSION = 'gz'

    #: Files with this extension will encrypt before writing to file, and
    #: decrypt after reading. The read/write methods therefore require a
    #: crypt_key
    CRYPT_EXTENSION = 'aes'

    #: Extensions reserved for compression and encryption
    RESERVED_EXTENSIONS = [COMPRESSED_EXTENSION,
                           CRYPT_EXTENSION]

    #: File names starting with this character will be tagged as hidden
    HIDDEN_STARTSWITH = '.'

    #: Extension separator. Period
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
        """
        Create a file path in home folder

        :param file_name: File name
        :type file_name: str
        :return: File
        :rtype: File
        """
        return cls.join(Folder.home(), file_name)

    @classmethod
    def _crypt_key(cls, crypt_key=None, password=None):
        """ Using a password will make a encryption_key combined with the
        internal class salt
        """
        if crypt_key and password:
            raise FileError('Use either crypt_key or password.')
        elif not crypt_key and not password:
            raise FileError('crypt_key or password missing')
        if crypt_key:
            return crypt_key
        else:
            return Crypt.key_from_password(cls._salt, password)

    @classmethod
    def make_file_name(cls,
                       stub,
                       extension,
                       is_compressed=False,
                       is_encrypted=False):
        if cls.EXTENSION_SEPARATOR in stub:
            raise FileError(f'Cannot add stub with extension '
                            f'separator in it: {stub}. '
                            f'Need a clean string for this')
        if cls.EXTENSION_SEPARATOR in extension:
            raise FileError(f'Cannot add extension with extension '
                            f'separator in it: {extension}. '
                            f'Need a clean string for this')
        new_names = [stub, extension]
        if is_compressed:
            new_names += [cls.COMPRESSED_EXTENSION]
        if is_encrypted:
            new_names += [cls.CRYPT_EXTENSION]
        return cls.EXTENSION_SEPARATOR.join(new_names)

    def __new__(cls, path_str, is_binary=False, *args, **kwargs):
        # TODO: Raise exception if reserved extensions are used inappropriately
        instance = Path.__new__(cls, path_str)
        if instance.exists():
            if instance.is_volume():
                raise FileError(f'Path is volume, not file: {path_str}')
            elif instance.is_folder():
                raise FileError(f'Path is existing folder, '
                                f'not file: {path_str}')
        instance._hidden = instance.name().startswith(cls.HIDDEN_STARTSWITH)
        instance._compressed = cls.COMPRESSED_EXTENSION \
                               in instance.extensions()
        instance._encrypted = cls.CRYPT_EXTENSION \
                              in instance.extensions()
        instance._json = cls.JSON_EXTENSION \
                         in instance.extensions()
        return instance

    def parts(self):
        """
        Get file parts, i.e. those separated by period

        :return: list
        """
        parts = self.name().split(self.EXTENSION_SEPARATOR)
        if self.is_hidden():
            parts = parts[1:]
        return parts

    def extensions(self):
        """
        Get file extensions

        :return: List of file extensions
        :rtype: list
        """
        return self.parts()[1:]

    def is_hidden(self):
        """
        Check if file is hidden, i.e. starts with a period

        :return: True if hidden, False if not
        :rtype: bool
        """
        return self._hidden

    def is_encrypted(self):
        """
        Check if file is encrypted, i.e. ends with reserved extension \'aes\'

        :return: True if encrypted, False if not
        :rtype: bool
        """
        return self._encrypted

    def is_compressed(self):
        """
        Check if file is compressed, i.e. has reserved extension \'gz\'

        :return: True if compressed, False if not
        :rtype: bool
        """
        return self._compressed

    def stub(self):
        """
        Get file stub, i.e. the part of the file name bar extensions

        :return: File stub
        :rtype: str
        """
        return self.parts()[0]

    def extension(self):
        """
        Get file extension, i.e. the extension which is not reserved.
        A file is only supposed to have one extension that does not indicate
        either compression or encryption.

        :raise FileError: If file has more than one not reserved extensions
        :return: File extension
        :rtype: str
        """
        extensions = self.extensions()
        extensions = [x for x in extensions
                      if x not in self.RESERVED_EXTENSIONS]
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
        """
        Get MD5 Checksum for the file

        :raise FileError: If file does not exist
        :return: MD5 Checksum
        :rtype: str
        """
        if not self.exists():
            raise FileError(f'Cannot make checksum '
                            f'if file does not exist: {self}')
        md5 = hashlib.md5()
        with open(self, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def delete(self, missing_ok=False):
        """
        Delete file

        :raise FileError: If file is missing, and ``missing_ok=False``
        :param missing_ok: Indicate if an exception should be raised if the
            file is missing. If True, an exception will not be raised
        :type missing_ok: bool
        :return: None
        """
        if self.exists():
            logger.debug(f'Delete file: {self}')
            os.unlink(self)
        elif not missing_ok:
            raise FileError(f'Tried to delete file '
                            f'that doesn\'t exist: {self}')

    def name(self):
        """
        Get file name

        :return: File name
        :rtype: str
        """
        return os.path.basename(self)

    def write(self, data, mode='w',
              crypt_key=None, password=None,
              human_readable=True, **kwargs):
        """
        Write data to file

        For encryption, use either ``crypt_key`` or ``password``. None or both
        will raise an exception. Encryption requires the file name to end with
        extension \'aes\'

        :raise FileError: If using ``crypt_key`` or ``password``, and the
            file does not have encrypted extension
        :param data: Data to write
        :type data: str or bytes
        :param mode: Write mode
        :type mode: str
        :param crypt_key: Encryption key
        :type crypt_key: bytes
        :param password: Password (will use class salt)
        :type password: str
        :param human_readable: JSON only, will write json to file with
            new lines and indentation
        :type human_readable: bool
        """
        # TODO: Require compression if file is encrypted?
        if self._encrypted:
            crypt_key = self._crypt_key(crypt_key, password)
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
                    logger.warning('On the fly encrypt/compress not '
                                   'implemented. There is an extra read/write '
                                   'from/to disk. In other words, '
                                   'this is a hack.')
                # TODO: Refactor to write once, but verify zlib/gzip
                #  compatibility
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
        """
        Read file

        If file is encrypted, use either ``crypt_key`` or ``password``.
        None or both will raise an exception. Encryption requires the file
        name to end with extension \'aes\'

        :raise FileError: If trying to decrypt a file without encryption
            extension
        :param mode: Read mode
        :param crypt_key: Encryption key
        :param password: Password (will use class salt)
        :return: data
        :rtype: str or bytes
        """
        if not self.exists():
            raise FileError(f'Cannot read from file '
                            f'that does not exist: {self}')
        if self._encrypted:
            crypt_key = self._crypt_key(crypt_key, password)
        elif crypt_key or password:
            raise FileError(f'File does not have crypt extension '
                            f'({self.CRYPT_EXTENSION}), but a crypt_key '
                            f'or password was sent as input to write.')
        if self._compressed:
            if self._encrypted:
                logger.warning('On the fly encrypt/compress not implemented. '
                               'There is an extra read/write from/to disk. '
                               'In other words, this is a hack.')
                # TODO: Refactor to read once, but
                #  verify zlib/gzip compatibility
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
        """
        Rename file

        :param new_name: New file name, including extension
        :return: A new File with the new file name
        :rtype: File
        """
        new_path = self.join(self.folder(), new_name)
        os.rename(self, new_path)
        return File(new_path)

    def folder(self):
        """
        Get the folder containing the file

        :return: Folder containing the file
        :rtype: Folder
        """
        return Folder(os.path.dirname(self))

    def files(self, pattern='*', recursive=False):
        """
        Get a list of all files in folder containing the file

        :param pattern: Wildcard or pattern
        :param recursive: Recursive flag. When True, all subfolders will be
            searched
        :return: List of files
        :rtype: list of File
        """
        files = self.folder().files(pattern='*', recursive=False)
        return [File(x) for x in files]

    def move(self, new_folder, new_name=None):
        """
        Move file to a new folder, and optionally a new name

        :param new_folder: New folder
        :type new_folder: Folder
        :param new_name: New file name (optional). If missing, the file will
            keep the same name
        :return: Moved file
        :rtype: File
        """
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
        """
        Copy file to a new folder, and optionally give it a new name

        :param new_folder: New folder
        :type new_folder: Folder
        :param new_name: New file name (optional). If missing, the file will
            keep the same name
        :return: Copied file
        :rtype: File
        """
        if self.folder() == new_folder:
            raise FileError(f'Cannot copy a file '
                            f'to the same folder: {new_folder}')
        new_folder.touch()
        if new_name:
            new_file = File.join(new_folder, new_name)
        else:
            new_file = File.join(new_folder, self.name())
        shutil.copyfile(self, new_file)
        return new_file

    def compress(self, delete_original=True):
        """
        Compress file

        :param delete_original: If True, original file will be deleted after
            compression
        :return: New compressed file, with extension \'gz\'
        :rtype: File
        """
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
        new_file.compression_percent = 100 * (old_size - new_file.size()) \
                                       / old_size
        logger.debug(f'Compressed with compression '
                     f'{new_file.compression_percent:.2f}')
        return new_file

    def decompress(self, delete_original=True, replace_if_exists=True):
        """
        Decompress file

        :param delete_original: If True, the original compressed file will be
            deleted after decompression
        :param replace_if_exists: If True, the decompressed file will replace
            any already existing file with the same name
        :return: Decompressed file
        :rtype: File
        """
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
        """
        Encrypt file

        :raise FileError: If file is already encrypted
        :param crypt_key: Encryption key
        :param delete_original: If True, the original unencrypted file will
            be deleted after encryption
        :return: Encrypted file
        :rtype: File
        """
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
        """
        Decrypt file

        :raise FileError: If file is not encrypted
        :param crypt_key: Encryption key
        :param delete_original: If True, the original encrypted file will
            be deleted after decryption
        :return: Decrypted file
        :rtype: File
        """
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
        """
        Generator for files in containing folder

        :raises PathError: If path does not exist
        :param pattern: Search pattern
        :param recursive: Recursive flag (when True, all subfolders will be
            searched)
        :type recursive: bool
        :returns: Generator of files in folder
        :rtype: generator of File
        """
        paths = self.folder().glob(pattern=pattern, recursive=recursive)
        return (File(x) for x in paths if x.is_file())


class FileError(Exception):
    pass
