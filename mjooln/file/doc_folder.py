import logging

from mjooln import Doc, File, Folder

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

    def __init__(self, folder_path):
        self._folder = Folder(folder_path)
        self._folder.touch()
        self._file = File.join(self._folder, self._file_name())
        if self._file.exists():
            self.read()
        else:
            self.write()

    def _file_name(self):
        return f'.{self._folder.name()}.json'

    def folder(self):
        return self._folder

    def file(self):
        return self._file

    def write(self):
        self._file.write(self.doc())

    def read(self):
        doc = self._file.read()
        self.add(doc)

    def empty(self):
        self._folder.empty()
        # Add the attribute file back to the folder
        self.write()

    def remove(self):
        self._file.delete()
        self._folder.remove()
