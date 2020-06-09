import pytest

from mjooln import Atom, AtomError, Zulu, Key, Identity


def test_segment():
    k = Key('some_key')
    z = Zulu()
    i = Identity()
    s = Atom(z, k, i)
    assert str(s) == f'{z}{Atom.SEPARATOR}{k}{Atom.SEPARATOR}{i}'
    assert s.key == k
    assert s.zulu == z
    assert s.identity == i
    ss = Atom(str(s))
    assert str(ss) == str(s)

    with pytest.raises(AtomError):
        Atom()
    with pytest.raises(AtomError):
        Atom(zulu=z)
    with pytest.raises(AtomError):
        Atom(zulu=z, identity=i)

    with pytest.raises(AtomError):
        Atom(f'{z}{k}{Atom.SEPARATOR}{i}')

    with pytest.raises(AtomError):
        Atom(f'{z}{Atom.SEPARATOR}{k}{i}')

    with pytest.raises(AtomError):
        Atom('This is not a segment')
