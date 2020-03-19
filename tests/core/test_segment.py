import pytest

from mjooln import Segment, SegmentError, Zulu, Key, Identity


def test_segment():
    k = Key('some_key')
    z = Zulu()
    i = Identity()
    s = Segment(z, k, i)
    assert str(s) == f'{z}{Segment.SEPARATOR}{k}{Segment.SEPARATOR}{i}'
    assert s.key == k
    assert s.zulu == z
    assert s.identity == i
    ss = Segment(str(s))
    assert str(ss) == str(s)

    with pytest.raises(SegmentError):
        Segment()
    with pytest.raises(SegmentError):
        Segment(zulu=z)
    with pytest.raises(SegmentError):
        Segment(zulu=z, identity=i)

    with pytest.raises(ValueError):
        Segment(f'{z}{k}{Segment.SEPARATOR}{i}')

    with pytest.raises(ValueError):
        Segment(f'{z}{Segment.SEPARATOR}{k}{i}')

    with pytest.raises(ValueError):
        Segment('This is not a segment')
