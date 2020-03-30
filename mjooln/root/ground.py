from mjooln import Root, Dic, Folder, File, RootError, Zulu, NotRootException

# TODO: A field can have split trees (identical, indexed, and with randomized where each leaf is)


class GroundProblem(Exception):
    pass


# TODO: Need Ground Elf to handle the different roots?
class Ground(Folder):
    """Folder wrapper with the ability to list roots within"""
    FILE_NAME = f'{File.HIDDEN_STARTSWITH}ground{File.EXTENSION_SEPARATOR}{File.JSON_EXTENSION}'

    @classmethod
    def search_for(cls):
        files = File.list(pattern=cls.FILE_NAME, recursive=True)
        return [cls(x.folder()) for x in files]

    @classmethod
    def _file(cls, folder):
        return File.join(folder, cls.FILE_NAME)

    @classmethod
    def is_ground(cls, folder):
        if not folder.exists() or not cls._file(folder).exists():
            return False
        else:
            return True

    @classmethod
    def settle(cls, folder, given_name='nn', **kwargs):
        if not folder.exists():
            raise GroundProblem(f'Cannot settle if the folder does not exist: {folder}')
        file = cls._file(folder)
        if file.exists():
            dic = file.read()
            if 'given_name' in dic:
                name_ = dic['given_name']
            else:
                name_ = 'nn'
            raise GroundProblem(f'This folder is already occupied by \'{name_}\'.')
        else:
            dic = {
                'given_name': given_name
            }
            if kwargs:
                dic.update(kwargs)
            file.write(dic)
            return cls(folder)

    @classmethod
    def settle_at_home(cls, name='unknown'):
        folder = Folder.home()
        return cls.settle(folder, name=name)

    @classmethod
    def home(cls):
        return cls(super(Ground, cls).home())

    @classmethod
    def elf(cls, path=None, **kwargs):
        if not path:
            folder = Folder.home()
        else:
            folder = Folder.elf(path)
        folder.touch()
        if not cls.is_ground(folder):
            return cls.settle(folder)
        else:
            return cls(folder)

    def __str__(self):
        return f'ground@{self.name()}'

    def __init__(self, folder):
        super().__init__()
        if not self.is_ground(folder):
            raise GroundProblem(f'Folder is not settled ground: {folder}')

    def bury(self, dic):
        # TODO: Refactor. At the moment it is something resembling a log.
        file = self._file(self)
        buried_dic = file.read()
        buried_dic[str(Zulu())] = dic
        file.write(buried_dic)

    def retrieve(self):
        file = self._file(self)
        return file.read()

    def unsettle(self):
        self._file(self).delete()

    def root(self, key):
        if self.is_root(key):
            return self.append(key)
        else:
            raise GroundProblem(f'Key \'{key}\' is not root in this ground (\'{self}\'). '
                                f'Try planting it or look somewhere else.')

    def is_root(self, key):
        folder = self.append(key)
        try:
            # TODO: Refactor to not use exception?
            _ = Root(folder)
            return True
        except NotRootException:
            return False

    def roots(self):
        paths = self.list()
        folders = [x for x in paths if x.is_folder()]
        roots = []
        for folder in folders:
            try:
                root = Root(folder)
                roots.append(folder)
            except RootError:
                pass
        return roots
