from mjooln import Doc, File


class DocFileError(Exception):
    pass


class DocFile(Doc):
    """
    Enables mirroring attributes to a JSON file

    .. note:: Meant for inheritance and more advanced functionality,
        not direct use

    .. warning:: May very well prove useless
    """

    def __init__(self, file_path, crypt_key=None, password=None, **kwargs):
        self._file = File(file_path)
        if self._file.is_encrypted():
            self._crypt_key = File._crypt_key(
                crypt_key=crypt_key,
                password=password)
        else:
            self._crypt_key = None

        if not self._file.extension() == 'json':
            raise DocFileError(f'Document file must be of type \'json\'. '
                               f'IE end with \'.json\', '
                               f'\'.json.gz\' or \'json.gz.aes\'. '
                               f'The input path does not: {file_path}')
        if self._file.exists():
            self.read()
        else:
            self.write()

    def add(self, dic_or_doc, ignore_private=True):
        super().add(dic_or_doc, ignore_private=ignore_private)
        self.write()

    def read(self, ignore_private=True):
        dic = self._file.read(crypt_key=self._crypt_key)
        self.add(dic, ignore_private=ignore_private)

    def write(self, ignore_private=True):
        dic = self.dic(ignore_private=ignore_private)
        self._file.write(dic, crypt_key=self._crypt_key)

    def file(self):
        return self._file

    def folder(self):
        return self._file.folder()

