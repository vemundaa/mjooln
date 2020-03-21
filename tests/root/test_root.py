import pytest
from mjooln.root.root import Root, RootError, NotRootException


def test_plant(tmp_folder):
    root = Root.plant(tmp_folder, 'my_root')
    assert root._key == 'my_root'
    file = root._file
    dic = file.read()
    assert dic['_key'] == 'my_root'
    assert dic['_species'] == 'root'
    assert file.folder().name() == 'my_root'

    root = Root(tmp_folder.append('my_root'))
    assert root._species == 'root'


def test_kwargs(tmp_folder):
    root = Root.plant(tmp_folder, 'my_root', one_argument='hey', another_argument=5.5)
    assert root._key == 'my_root'
    file = root._file
    dic = file.read()
    assert dic['one_argument'] == 'hey'
    assert dic['another_argument'] == 5.5

    root = Root(tmp_folder.append('my_root'))
    assert root.one_argument == 'hey'
    assert root.another_argument == 5.5


def test_class_attributes(tmp_folder):

    class MyRoot(Root):

        def __init__(self, folder_path,
                     compressed=False, encrypted=False, default=False):
            self.one_argument = 'there it is'
            self.another = 5.5
            super().__init__(folder_path,
                             compressed=compressed, encrypted=encrypted, default=default)

    my_root = MyRoot.plant(tmp_folder, 'best_root')
    assert my_root.one_argument == 'there it is'
    assert my_root.another == 5.5

    my_root = MyRoot(tmp_folder.append('best_root'))
    assert my_root.one_argument == 'there it is'
    assert my_root.another == 5.5

    my_root.uproot()
    with pytest.raises(NotRootException):
        _ = MyRoot(tmp_folder.append('best_root'))

    my_root = MyRoot.plant(tmp_folder, 'best_root')

    my_root._file.delete()
    with pytest.raises(NotRootException):
        _ = MyRoot(tmp_folder.append('best_root'))

    my_root._folder.remove()
    with pytest.raises(NotRootException):
        _ = MyRoot(tmp_folder.append('best_root'))

