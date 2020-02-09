from mjooln import Folder


def test_append():
    f = Folder('.')
    assert f.append('a') == str(f) + '/a'
    assert f.append('a', 'b') == str(f) + '/a/b'
    assert f.append('a', 'b', 'c') == str(f) + '/a/b/c'
    assert f.append(['a']) == str(f) + '/a'
    assert f.append(['a', 'b']) == str(f) + '/a/b'
    assert f.append(['a', 'b', 'c']) == str(f) + '/a/b/c'
