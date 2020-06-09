from mjooln import Path, Folder, Key
from mjooln.tree.root import Root


class GroundProblem(Exception):
    pass


class NoGround(Exception):
    pass

#     CAVE = 'cave'
#     SPECIES = CAVE
#
#     @classmethod
#     def is_cave(cls, folder):
#         if cls.is_root(folder):
#             root = Root(folder)
#             if root.species() == cls.SPECIES:
#                 return True
#         return False
    #
    # @classmethod
    # def plant(cls, folder, key, **kwargs):
    #     raise CaveProblem('Cannot plant a cave. Use dig().')
    #
    # @classmethod
    # def dig(cls, folder):
    #     super(Cave, cls).plant(folder, key=cls.CAVE)
    #
    # def uproot(self, with_force=False, key=None):
    #     raise CaveProblem('Cannot uproot a cave. You need to unsettle '
    #                       'ground for this, which is rather complicated.')


class Ground(Folder):

    _CAVE = 'cave'
    _GROUND_KEY = 'ground_key'
    STARTSWITH = f'.ground{Key.OUTER_SEPARATOR}'

    @classmethod
    def _ground_folder(cls, path, key):
        name = ''.join([cls.STARTSWITH, key])
        return Folder.join(path, name)

    @classmethod
    def _key_from_ground_folder(cls, folder):
        return folder.name().replace(cls.STARTSWITH, '')

    @classmethod
    def _find_ground(cls, folder):
        paths = folder.list(cls.STARTSWITH + '*')
        if len(paths) > 1:
            raise GroundProblem(f'Found multiple grounds: {paths}')
        elif len(paths) == 0:
            raise NoGround(f'No ground found in folder: {folder}')
        ground_folder = Folder.elf(paths[0])
        return cls._key_from_ground_folder(ground_folder)

    @classmethod
    def _has_ground(cls, folder):
        paths = folder.list(cls.STARTSWITH + '*')
        return len(paths) > 0

    @classmethod
    def settle(cls, path, key):
        path = Path.elf(path)
        if not path.exists():
            raise GroundProblem(f'Cannot settle ground in non existent '
                                f'path: {path}')
        if not path.is_folder():
            raise GroundProblem(f'Cannot settle ground if path '
                                f'is not folder: {path}')
        if cls._has_ground(path):
            raise GroundProblem(f'This folder has already been settled: {path}')

        key = Key.elf(key)
        ground_folder = cls._ground_folder(path, key)
        ground_folder.create()
        Root.plant(ground_folder, 'cave', ground_key=key)
        return cls(path)

    def __init__(self, folder):
        super(Ground, self).__init__()
        key = self._find_ground(folder)
        ground_folder = self._ground_folder(self, key)
        cave_folder = Folder.join(ground_folder, self._CAVE)
        cave = Root(cave_folder)
        if not cave.key() == self._CAVE:
            raise NoGround(f'Invalid key in cave: {cave.key()}')
        try:
            self.key = cave.dic()[self._GROUND_KEY]
        except KeyError:
            raise NoGround(f'Ground key not found in cave')
        self.zulu = cave.zulu()
        self.identity = cave.identity()
        self.cave = cave.folder()

    def glob(self, pattern='*', recursive=False):
        ground_folder = self._ground_folder(self, self.key)
        return (x for x in super().glob() if not x.startswith(ground_folder))

    def roots(self):
        roots = Root.find_all(Folder(str(self)))
        return [x for x in roots if x.key != self._CAVE]
