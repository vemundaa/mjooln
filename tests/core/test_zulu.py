import pytest
import pytz
from datetime import datetime as dt

from mjooln import Zulu, ZuluError


def test_zulu_datetime():
    a = dt.now()
    with pytest.raises(ZuluError):
        Zulu(a)
    b = a.replace(tzinfo=pytz.utc)
    c = Zulu(b)
    assert c.hour == a.hour


def test_zulu_local():
    a = Zulu()
    b = a.to_local()
    assert not isinstance(b, Zulu)

    c = Zulu.from_unaware_local(b.replace(tzinfo=None))
    d = c.to_local()
    assert b.hour == d.hour


def test_parse_zulu():
    zstr = '20200106T073022u399776Z'
    z = Zulu(zstr)
    assert str(z) == zstr


def test_zulu_isostr():
    zstr = '20200106T073022u399776Z'
    z = Zulu(zstr)
    isostr = '2020-01-06T07:30:22.399776+00:00'
    assert z.iso() == isostr
    z = Zulu.parse_iso(isostr)
    assert z.iso() == isostr
    assert str(z) == zstr


def test_zulu_str():
    # TODO: Test convenience methods (parse, elf etc)
    z = Zulu(2019, 5, 5)
    assert str(z) == '20190505T000000u000000Z'
    z = Zulu(2019, 5, 5, 6, 6, 7)
    assert str(z) == '20190505T060607u000000Z'
    z = Zulu(2019, 5, 5, 1, 1, 1, 23342, pytz.utc)
    assert str(z) == '20190505T010101u023342Z'
    assert z.microsecond == 23342
    assert z.str.microsecond == '023342'

    z = Zulu(2019, 5, 5)
    assert z.year == 2019
    assert z.day == 5
    assert z.str.day == '05'
    assert z.str.second == '00'
    assert z.str.date == '20190505'
    assert z.str.time == '000000'


def test_zulu_elf():
    z = Zulu(2020, 5, 23, 11, 22, 33)
    zstr = str(z)
    isostr = z.iso()
    dt = z.to_local()
    dtt = z.to_tz('Pacific/Easter')

    assert str(z) == str(Zulu(zstr))
    assert str(z) == str(Zulu.parse_iso(isostr))
    assert str(z) == str(Zulu(dt))
    assert str(z) == str(Zulu(dtt))

    assert str(z) == str(Zulu.elf(zstr))
    assert str(z) == str(Zulu.elf(isostr))
    assert str(z) == str(Zulu.elf(dt))
    assert str(z) == str(Zulu.elf(dtt))

    dt = dt.replace(tzinfo=None)
    assert str(z) == str(Zulu.elf(dt, tz_assume='local'))
    dtz = z.to_tz('utc').replace(tzinfo=None)
    assert str(z) == str(Zulu.elf(dtz, tz_assume='utc'))
    assert str(z) == str(Zulu.elf(z))



