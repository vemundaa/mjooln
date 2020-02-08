from mjooln import Dic, Doc, Zulu, Segment


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


def test_ignore_startswith():
    d = Dic()
    d._a = 'no'
    d.b = 4
    d.c = 6
    assert d.dic() == {'b': 4, 'c': 6}
    assert d._a == 'no'


def test_exists_only():
    d = Dic()
    d.a = 2
    d.b = 3
    d.c = 4
    d.add_dic({'b': 5, 'bb': 6}, existing_only=True)
    assert d.dic() == {'a': 2, 'b': 5, 'c': 4}


def test_force_match():
    d = Dic()
    d.a = 2
    d.b = 3
    d.c = 4
    d.add_dic({'a': 5, 'b': 6}, force_equal=True)
    assert d.dic() == {'a': 5, 'b': 6}


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
