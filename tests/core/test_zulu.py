import pytest
import pytz

from mjooln import Zulu


def test_zulu():
    zstr = '20200106T073022u399776Z'
    z = Zulu(zstr)
    assert str(z) == zstr
    isostr = '2020-01-06T07:30:22.399776+00:00'
    assert z.to_iso_string() == isostr
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

