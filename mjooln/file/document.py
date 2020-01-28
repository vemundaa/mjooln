from mjooln import Doc, File


class DocumentError(Exception):
    pass


class Document(File, Doc):

    ALLOW_EDIT = True
    FILE_IS_BOSS = True

    @classmethod
    def create(cls, file, dic=None, doc=None):
        if dic and doc:
            raise DocumentError('Cannot create Document with both '
                                'dic and doc as input. Choose one, please.')
        if not dic and not doc:
            raise DocumentError('Cannot create Document with neither dic or doc as input.')
        if file.exists():
            raise DocumentError(f'Cannot create new document when file already exists: {file}. '
                                f'Use elf() for softer approach.')
        file.folder().touch()
        doc_file = cls(file)
        if dic:
            doc_file.add_dic(dic)
        if doc:
            doc_file.add_doc(doc)
        doc_file.write()
        return doc_file

    @classmethod
    def elf(cls, file, dic=None, doc=None):
        file = File.elf(file)
        if file.exists():
            if cls.FILE_IS_BOSS:
                return cls(file)
            else:
                file.delete()
        return cls.create(file, dic=dic, doc=doc)

    def __new__(cls, file, *args, **kwargs):
        if not file.endswith('.json') and not file.endswith('.json.gz'):
            raise DocumentError(f'Document file name must end with .json or .json.gz. '
                                f'The input path doesnt: {file}')
        return File.__new__(cls, file)

    def __init__(self, file, *args, **kwargs):
        Doc.__init__(self)
        File.__init__(self)
        if self.exists():
            self.read()

    def dic(self):
        dic = super().dic()
        # TODO: Improve this solution
        local_vars = [x for x in dic if x.startswith('_Document__')]
        for local in local_vars:
            dic.pop(local)
        return dic

    def read(self):
        if self.is_compressed():
            tmp_file = File(self.decompress(delete_original=False))
            doc = tmp_file.read()
            tmp_file.delete()
        else:
            doc = super().read()
        self.add_doc(doc)

    def write(self, content=None, mode='w'):
        if self.ALLOW_EDIT or not self.exists():
            if self.is_compressed():
                tmp_file = self.decompress()
                tmp_file.write(content=self.doc())
                _ = tmp_file.compress()
            else:
                super().write(content=self.doc(), mode='w')
        else:
            raise DocumentError(f'Cannot write to existing file: {self}.'
                                f'Set ALLOW_EDIT=True to allow this.')


class Ledger(Document):

    def __init__(self, file, text=None, number=None):
        self.text = text
        self.number = number
        Document.__init__(self, file)


if __name__ == '__main__':
    l = Ledger('ledger.json')
    l.dev_print()
    l.number = 44
    l.write()
    l.dev_print()

