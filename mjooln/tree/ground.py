from mjooln import Path, Folder, Key
from mjooln.tree.root import Root


class GroundProblem(Exception):
    pass


class NoGround(Exception):
    pass


class Ground(Folder):
    # TODO: Revise after ground can be used to tag drives
    """
    Custom hidden folder marking a specific folder as ``Ground``.

    Intended usage is for marking a location in a file system or network drive
    for simplified access. Roots in folder may be accessed directly, and
    attributes and statistics regarding all roots in the underlying folder
    structure may be stored in the ``cave``, which is a root folder hidden
    under ``ground``.
    """

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
    def is_in(cls, folder):
        """
        Check if folder is settled ground

        :raise GroundProblem: If folder contains multiple grounds, which is
            is a major problem
        :param folder: Folder to check
        :type folder: Folder
        :return: True if folder contains ground, False if not
        :rtype: bool
        """
        num_paths = len(folder.list(cls.STARTSWITH + '*'))
        if num_paths == 0:
            return False
        elif num_paths == 1:
            return True
        else:
            raise GroundProblem(f'Folder has multiple grounds: {folder}')

    @classmethod
    def settle(cls, folder, key):
        """
        Create new ground in the specified folder path, with the given key.

        :param folder: Folder to settle
        :type folder: Folder
        :param key: Ground key
        :type key: Key
        :return: Settled ground
        :rtype: Ground
        """
        folder = Folder.elf(folder)
        if not folder.exists():
            raise GroundProblem(f'Cannot settle ground in non existent '
                                f'path: {folder}')
        if cls.is_in(folder):
            raise GroundProblem(f'This folder has already been '
                                f'settled: {folder}')

        key = Key.elf(key)
        ground_folder = cls._ground_folder(folder, key)
        ground_folder.create()
        Root.plant(ground_folder, 'cave', ground_key=key)
        return cls(folder)

    def __init__(self, folder):
        super(Ground, self).__init__()
        key = self._find_ground(folder)
        ground_folder = self._ground_folder(self, key)
        cave_folder = Folder.join(ground_folder, self._CAVE)
        cave = Root(cave_folder)
        if not cave.key() == self._CAVE:
            raise NoGround(f'Invalid key in cave: {cave.key()}')
        try:
            ground_key = cave.dic()[self._GROUND_KEY]
            if not ground_key == key:
                raise NoGround(f'Ground key mismatch. '
                               f'Expected from folder name: {key}. '
                               f'Found in cave: {ground_key}')
            self.key = Key.elf(ground_key)
        except KeyError:
            raise NoGround(f'Ground key not found in cave')
        self.zulu = cave.zulu()
        self.identity = cave.identity()
        self.cave = cave.folder()

    def glob(self, pattern='*', recursive=False):
        ground_folder = self._ground_folder(self, self.key)
        return (x for x in super().glob() if not x.startswith(ground_folder))

    def roots(self):
        # TODO: Add max depth of search
        # TODO: Add specific folders option (if implemented)
        """
        Find all roots recursively from ground folder

        :return: List of all roots
        :rtype: [Root]
        """
        roots = Root.find_all(Folder(str(self)))
        return [x for x in roots if x.key != self._CAVE]
