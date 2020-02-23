import random
import string

from mjooln.path.file import File


class TextFileError(Exception):
    pass


class TextFile(File):

    def write(self, text, *args, **kwargs):
        if not isinstance(text, str):
            raise TextFileError(f'Input data is not string, instead it is: {type(text)}')
        if self._compressed:
            super()._write_compressed(content=text)
        else:
            super()._write(content=text, mode='wt')

    def append(self, text):
        if not isinstance(text, str):
            raise TextFileError(f'Input data is not string, instead it is: {type(text)}')
        if self._compressed:
            raise TextFileError('Cannot append to compressed file.')
        else:
            super()._write(content=text, mode='at+')

    def read(self, *args, **kwargs):
        if self._compressed:
            content = super()._read_compressed()
            if isinstance(content, bytes):
                content = content.decode()
            return content
        else:
            return super()._read(mode='rt')

    @classmethod
    def new(cls, path, text):
        file = TextFile(path)
        if file.exists():
            raise TextFileError(f'File already exists: {file}')
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
            raise TextFileError(f'File already exists: {file}')
        return file


if __name__ == '__main__':
    f = TextFile('hey.txt.gz')
    f.write('something best')
    print(f.read())