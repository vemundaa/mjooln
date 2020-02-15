from mjooln import Key, Root, Folder, RootError

# TODO: Make linked fields. Either a copy or addition.
# TODO: Field should inherit RootFolder, and handle the different types of root.
# TODO: A field can have split trees (identical, indexed, and with randomized where each leaf is)


class FieldError(Exception):
    pass


class Field(Root):

    @classmethod
    def plant(cls, folder, **kwargs):
        raise FieldError('Cannot plant a field. Use \'settle\'. '
                         'When settled, you can plant roots in a field '
                         'using \'plant_root\', with key (root name) '
                         'as input.')

    @classmethod
    def settle(cls, folder, name='', **kwargs):
        if cls._file(folder).exists():
            return cls(folder)
        return super().plant_with_force(folder, type='field', given_name=name, **kwargs)

    @classmethod
    def settle_at_home(cls):
        folder = Folder.home()
        return cls.settle(folder, name=f'Home Sweet Home')

    def __str__(self):
        return self.name()

    def name(self):
        if self.given_name:
            return self.given_name
        else:
            return super().name()

    def __init__(self, folder):
        self.type = None
        self.given_name = ''
        Root.__init__(self, folder)
        if not self.type == 'field':
            raise FieldError(f'Root is not a field. Type mismatch. '
                             f'Should be \'field\', but is \'{self.type}\'. '
                             f'This probably means you\'ve tried to settle '
                             f'a field in an existing root.')

    def plant_root(self, key, **kwargs):
        key = Key(key)
        folder = self.append(key)
        return Root.plant(folder, **kwargs)

    def root(self, key):
        key = Key(key)
        return Root(self.append(key))

    def roots(self):
        paths = self.list()
        folders = [x for x in paths if x.is_folder()]
        roots = []
        for folder in folders:
            try:
                root = Root(folder)
                roots.append(root)
            except RootError:
                pass
        return roots


if __name__ == '__main__':
    field = Field.home()
    field.dev_print()
    # r1 = field.plant_root('test1')
    # r2 = field.plant_root('test2')
    for r in field.roots():
        r.dev_print()

    r1 = field.root('test1')
