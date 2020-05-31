import pytest
from mjooln.root.root import Root, RootError, NotRootException, File


def test_plant(tmp_folder):
    root = Root.plant(tmp_folder, 'my_root')
    assert root._root.key == 'my_root'
    file = root._file
    dic = file.read()
    assert dic['_root'].key == 'my_root'
    assert file.folder().name() == 'my_root'

    root = Root(tmp_folder.append('my_root'))
    assert root._root.key == 'my_root'


def test_kwargs(tmp_folder):
    root = Root.plant(tmp_folder,
                      'my_root',
                      one_argument='hey',
                      another_argument=5.5)
    assert root._root.key == 'my_root'
    file = root._file
    dic = file.read()
    assert dic['one_argument'] == 'hey'
    assert dic['another_argument'] == 5.5

    root = Root(tmp_folder.append('my_root'))
    assert root.one_argument == 'hey'
    assert root.another_argument == 5.5


def test_class_attributes(tmp_folder):

    class MyRoot(Root):

        def __init__(self, folder_path):
            # Add default arguments. Can be changed with plant
            self.one_argument = 'there it is'
            self.another = 5.5
            super().__init__(folder_path)

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


def test_elf(tmp_folder):
    folder = tmp_folder.append('not_root_yet')
    folder.create()
    root = Root.elf(folder)
    assert root._root.key == 'not_root_yet'
    root._root.key = 'other_root'
    with pytest.raises(RootError):
        root.write()
    file = root._file
    dic = dict()
    dic['key'] = 'other_root'
    dic['identity'] = root._root.identity
    dic['zulu'] = root._root.zulu
    dic2 = dict()
    dic2['_root'] = dic
    file.write(dic2)
    with pytest.raises(RootError):
        Root.elf(folder)


