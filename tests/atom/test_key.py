import pytest

from mjooln import Key, KeyFormatError


def test_key():
    key = Key('some_key')
    assert key == 'some_key'
    with pytest.raises(KeyFormatError):
        Key('Invalidkey')
    with pytest.raises(KeyFormatError):
        Key('invalid key')
    with pytest.raises(KeyFormatError):
        Key('3invalidkey')
    with pytest.raises(KeyFormatError):
        Key('_invalidkey')
    with pytest.raises(KeyFormatError):
        Key('invalid___separator')

    assert ['a', 'b', 'c'] == Key('a__b__c').parts()



