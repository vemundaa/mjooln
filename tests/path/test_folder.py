import pytest
import mjooln as mj


def test_append():
    f = mj.Folder('.')
    assert f.append('a') == str(f) + '/a'
    assert f.append('a', 'b') == str(f) + '/a/b'
    assert f.append('a', 'b', 'c') == str(f) + '/a/b/c'
    assert f.append(['a']) == str(f) + '/a'
    assert f.append(['a', 'b']) == str(f) + '/a/b'
    assert f.append(['a', 'b', 'c']) == str(f) + '/a/b/c'


def test_list(tmp_folder):
    folder = tmp_folder
    f1 = folder.append('f1')
    assert len(folder.folders()) == 0
    f1.touch()
    assert len(folder.folders()) == 1
    file = mj.File.join(folder, 'dummy.txt')
    file.write('test')
    assert len(folder.folders()) == 1
    assert len(folder.list()) == 2
    f2 = folder.append('f2')
    assert len(folder.list()) == 2
    f2.create()
    assert len(folder.list()) == 3
    with pytest.raises(mj.FolderError):
        f2.create()


