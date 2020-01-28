import pytest

from mjooln import Dic, Doc, JSON, Zulu, Segment


def test_dic():
    d = Dic()
    d.a = 3
    d.b = 4
    assert d.dic() == {'a': 3, 'b': 4}
    d = d.dic()
    dd = Dic()
    dd.add_dic(d)
    assert dd.dic() == d
    assert dd.a == 3
    assert dd.b == 4


def test_dic_zulu():
    z = Zulu()
    d = Dic()
    d.z = z
    dd = d.dic()
    assert dd['z'] == z


def test_doc():
    d = Doc()
    d.a = 5
    d.b = 'five'
    seg = Segment(key='dummy')
    d.s = seg
    d.z = Zulu()
    dd = d.doc()
    ddd = Doc()
    ddd.add_doc(dd)
    assert d.a == ddd.a
    assert d.b == ddd.b
    assert d.z == ddd.z
    assert str(d.s) == str(seg)
