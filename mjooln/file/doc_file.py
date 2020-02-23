from mjooln import Doc, File


class DocFileError(Exception):
    pass


class DocFile(Doc):

    def __init__(self, file_path, *args, **kwargs):
        self._file = File(file_path)
        if not self._file.extension() == 'json':
            raise DocFileError(f'Document file must be of type \'json\'. IE end with \'.json\', '
                               f'\'.json.gz.\' or \'json.gz.aes\'. '
                               f'The input path doesnt: {file_path}')
        if self._file.is_encrypted() or self._file.is_compressed():
            raise DocFileError(f'Compression and encryption not implemented for DocFile.')
        if self._file.exists():
            self.read()
        else:
            self.write()

    def add(self, dic_or_doc):
        super().add(dic_or_doc)
        self.write()

    def read(self, ):
        doc = self._file.read_text()
        self.add(doc)

    def write(self):
        doc = self.doc()
        self._file.write_text(doc)

    def file(self):
        return self._file

    def folder(self):
        return self._file.folder()


class Ledger(DocFile):

    def __init__(self, file, text=None, number=None):
        self.text = text
        self.number = number
        super().__init__(file)


if __name__ == '__main__':
    l = Ledger('ledger.json.gz')
    l.dev_print()
    l.number = 44
    l.write()
    l.dev_print()

