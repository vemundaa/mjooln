from mjooln import Path, Folder, Key, Atom
from mjooln.tree.root import Root


class GroundProblem(Exception):
    pass


class NoGround(Exception):
    pass


class Cave(Root):

    CAVE = 'cave'
    SPECIES = CAVE

    def is_cave(cls, folder):
        if cls.is_root(folder):
            root = Root(folder)
            if root.species() == cls.SPECIES:
                return True
        return False


class Ground(Folder):

    STARTSWITH = '.ground'

    @classmethod
    def _folder_name(cls, key):
        return Key.OUTER_SEPARATOR.join([cls.STARTSWITH, key])

    @classmethod
    def _parse_folder_name(cls, folder):

    @classmethod
    def _find_ground(cls, folder):
        folder = Folder.elf(folder)
        paths = folder.list(cls.STARTSWITH + '*')
        if len(paths) > 1:
            raise GroundProblem(f'Found multiple grounds: {paths}')
        elif len(paths) == 0:
            raise NoGround(f'No ground found in folder: {folder}')

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
            raise GroundProblem(f'This folder has already been settled')

        key = Key.elf(key)
        folder = Folder.join(path, cls._folder_name(key))
        folder.create()
        Cave.plant(folder, key)
        return cls(folder)

    def __init__(self, folder):
        super(Ground, self).__init__(folder)
        cave = [x for x in self.folders() if Cave.is_cave(x)]
        if len(cave) > 1:
            raise NoGround(f'Found multiple caves in folder: {self}')
        if len(cave) == 0:
            raise NoGround(f'Found no caves in folder: {self}')
        cave = cave[0]
        self.key = cave.key()
        self.zulu = cave.zulu()
        self.identity = cave.identity()
        self.cave = cave.folder()




