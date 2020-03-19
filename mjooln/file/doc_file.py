from mjooln import Doc, File


class DocFileError(Exception):
    pass


class DocFile(Doc):

    def __init__(self, file_path, key=None, password=None, **kwargs):
        self._file = File(file_path)
        if self._file.is_encrypted():
            self._key = File.key_from_key_or_password(key=key, password=password)
        else:
            self._key = None

        if not self._file.extension() == 'json':
            raise DocFileError(f'Document file must be of type \'json\'. IE end with \'.json\', '
                               f'\'.json.gz.\' or \'json.gz.aes\'. '
                               f'The input path doesnt: {file_path}')
        # if self._file.is_encrypted() or self._file.is_compressed():
        #     raise DocFileError(f'Compression and encryption not implemented for DocFile.')
        if self._file.exists():
            self.read()
        else:
            self.write()

    def add(self, dic_or_doc):
        super().add(dic_or_doc)
        self.write()

    def read(self, ):
        dic = self._file.read(key=self._key)
        self.add(dic)

    def write(self):
        dic = self.dic()
        self._file.write(dic, key=self._key)

    def file(self):
        return self._file

    def folder(self):
        return self._file.folder()


class Ledger(DocFile):

    def __init__(self, file, password=None, text=None, number=None):
        self.text = text
        self.number = number
        super().__init__(file, password=password)


if __name__ == '__main__':
    l = Ledger('ledger.json.gz.aes', password='test')
    l.dev_print()
    l.number += 33
    l.text = 'Some text you have'
    l.write()
    l.dev_print()

