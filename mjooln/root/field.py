from mjooln import Root

# TODO: Make linked fields. Either a copy or addition.
# TODO: Field should inherit RootFolder, and handle the different types of root.
# TODO: A field can have split trees (identical, indexed, and with randomized where each leaf is)


class Field(Root):

    TYPE = 'field'

    def roots(self):
        folders = self.list()
        return [Root(x) for x in folders if self.is_root(x)]


