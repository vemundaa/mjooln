# TODO: Make leaf handle the different file types, and also how to load them from the given root
import logging
import pandas as pd

from mjooln import File, Segment
from mjooln.core.crypt import CryptError

logger = logging.getLogger(__name__)


class NotALeafError(Exception):
    pass


class LeafError(Exception):
    pass


class Leaf:
    """ Existing file within a tree that follows segment naming."""

    EXTENSION = None

    def __init__(self, file, **kwargs):
        try:
            self._file = File.elf(file)
            self._extension = self._file.extension()
            self._segment = Segment(self._file.stub())
            if self.EXTENSION and not self._extension == self.EXTENSION:
                raise NotALeafError(f'File does not have required extension '
                                    f'\'{self.EXTENSION}\': {self._file}')
        except ValueError as ve:
            raise NotALeafError(f'File is not a leaf: {file}. '
                                f'Original error: {ve}')

    def file(self):
        return self._file

    def segment(self):
        return self._segment

    def feel(self, crypt_key=None):
        """Read file contents"""
        try:
            data = self._file.read(crypt_key=crypt_key)
        except CryptError as ce:
            raise LeafError(f'Invalid or missing encryption key while '
                            f'trying to feel \'{self._file}\'. Original error: {ce}')
        return data

    def pick(self, crypt_key=None):
        """Read file contents and delete file after"""
        data = self.feel(crypt_key=crypt_key)
        self._file.delete()
        return data

    def shape(self, compress=False, encrypt=False, crypt_key=None):
        try:
            if not self._file.is_compressed() and compress:
                if self._file.is_encrypted():
                    self._file = self._file.decrypt(crypt_key)
                self._file = self._file.compress()
            elif self._file.is_compressed() and not compress:
                if self._file.is_encrypted():
                    self._file = self._file.decrypt(crypt_key)
                self._file = self._file.decompress()
            if not self._file.is_encrypted() and encrypt:
                self._file = self._file.encrypt(crypt_key)
            elif self._file.is_encrypted() and not encrypt:
                self._file = self._file.decrypt(crypt_key)
        except CryptError as ce:
            raise LeafError(f'Invalid or missing encryption key while '
                            f'attempting reshape of {self._file}. Original error: {ce}')

    def prune(self, folder):
        if not folder:
            raise LeafError(f'Cannot prune leaf without input folder. '
                            f'Current folder is: {self._file.folder()}')
        if not self._file.folder() == folder:
            self._file = self._file.move(folder)
            logger.debug(f'Move leaf: {self._segment}')


