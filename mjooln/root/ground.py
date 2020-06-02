from mjooln import Root, Dic, Folder, File, RootError, Zulu, NotRootException

# TODO: A field can have split trees (identical,
#  indexed, and with randomized where each leaf is)


class GroundProblem(RootError):
    pass


class NotGroundException(NotRootException):
    pass


class Ground(Root):

    HOME_GROUND = 'ground_at_home'
    GROUND = 'ground'
    SPECIES = GROUND

    @classmethod
    def is_ground(cls, folder):
        try:
            cls(folder)
            return True
        except NotRootException:
            return False

    @classmethod
    def plant(cls, folder, key, **kwargs):
        raise GroundProblem('Cannot plant ground. Use settle()')

    @classmethod
    def uproot(self, with_force=False, key=None):
        raise GroundProblem('Cannot uproot ground. Use unsettle()')

    @classmethod
    def settle(cls, folder, key, name='nn', **kwargs):
        return super(Ground, cls).plant(folder=folder,
                                        key=key,
                                        name=name,
                                        **kwargs)

    @classmethod
    def settle_at_home(cls):
        # TODO: Consider the value of this.
        folder = Folder.home()
        return cls.settle(folder,
                          key=cls.HOME_GROUND,
                          name=cls.HOME_GROUND)

    def __init__(self, folder):
        self.name = 'nn'
        super(Ground, self).__init__(folder)

    def __str__(self):
        return f'{self.name}@{self.folder()}'

    def unsettle(self, with_force=False, key=None):
        super(Ground, self).uproot(with_force=with_force, key=key)

