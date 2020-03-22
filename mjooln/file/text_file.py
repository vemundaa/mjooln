import random
import string

from mjooln.path.file import File


class TextFileError(Exception):
    pass


class TextFile(File):

    def write(self, text, crypt_key=None, password=None, **kwargs):
        if not isinstance(text, str):
            raise TextFileError(f'Input data is not string, instead it is: {type(text)}')
        super().write(text, mode='wt', crypt_key=crypt_key, password=password)

    def append(self, text, crypt_key=None, password=None, **kwargs):
        if not isinstance(text, str):
            raise TextFileError(f'Input data is not string, instead it is: {type(text)}')
        if self.is_compressed() or self.is_encrypted():
            written_text = super().read(mode='rt', crypt_key=crypt_key, password=password)
            text = written_text + text
            super().write(text, mode='wt', crypt_key=crypt_key, password=password)
        else:
            super().write(text, mode='at+')

    def read(self, crypt_key=None, password=None, **kwargs):
        return super().read(mode='rt', crypt_key=crypt_key, password=password)

    def compress(self, delete_original=True):
        # Override super to return text file object
        # TODO: Possible to avoid this hack?
        return TextFile(super().compress(delete_original=delete_original))

    def decompress(self, delete_original=True, replace_if_exists=True):
        # Override super to return text file object
        return TextFile(super().decompress(delete_original=delete_original,
                                           replace_if_exists=replace_if_exists))

    def encrypt(self, crypt_key, delete_original=True):
        # Override super to return text file object
        return TextFile(super().encrypt(crypt_key=crypt_key, delete_original=delete_original))

    def decrypt(self, crypt_key, delete_original=True):
        # Override super to return text file object
        return TextFile(super().decrypt(crypt_key=crypt_key, delete_original=delete_original))

    @classmethod
    def new(cls, path, text):
        file = TextFile(path)
        if file.exists():
            raise TextFileError(f'File already exists: {file}')
        else:
            file.write(text=text)
            return file

    @classmethod
    def dev_create_random(cls, path_str, num_chars=1000):
        text = ''.join(random.choices(string.ascii_uppercase + string.digits + '\n',
                                      k=num_chars))
        file = cls(path_str)
        if not file.exists():
            file.write(text)
        else:
            raise TextFileError(f'File already exists: {file}')
        return file
