import logging

from mjooln.core.dic_doc import Doc
from mjooln.path.folder import Folder
from mjooln.file.doc_file import DocFile

logger = logging.getLogger(__name__)


class DocFolderError(Exception):
    pass


class DocFolder(Doc):
    """ Combination of a folder and a json file containing the attributes of the object.

    The json file name is '.<folder_name>.json', and is put within the folder.
    """

    @classmethod
    def home(cls):
        return cls(Folder.home())

    def __init__(self,
                 folder_path,
                 compressed=False,
                 encrypted=False,
                 key=None,
                 password=None,
                 **kwargs):
        self._folder = Folder(folder_path)
        self._folder.touch()
        _file = File(self._file_path(compressed=compressed, encrypted=encrypted))
        DocFile.__init__(_file, key=key, password=password)

    def _file_path(self, compressed, encrypted):
        file_name = f'.{self._folder.name()}.json'
        if compressed:
            file_name += '.gz'
        if encrypted:
            file_name += '.aes'
        return File.join(self, file_name)

    def folder(self):
        return self._folder

    def file(self):
        return self._file

    def write(self):
        self._file.write(self.dic())

    def read(self):
        dic = self._file.read()
        self.add(dic)

    def empty(self):
        self._folder.empty()
        # Add the attribute file back to the folder
        self.write()

    def remove(self):
        self._file.delete()
        self._folder.remove()
