import pytest

from mjooln import Identity, IdentityError


def test_identity():
    id1 = Identity()
    id2 = Identity(str(id1))
    assert id1 == id2
    id1 = Identity()
    id2 = Identity()
    id3 = Identity()
    with pytest.raises(IdentityError):
        Identity(id1)
    assert Identity.elf(id1) == id1
    idstr = f'Some {id1} thing with {id2} identities {id3} spread in between'
    assert Identity.find_all(idstr) == [id1, id2, id3]
    with pytest.raises(IdentityError):
        id1 = Identity.find_one('No id here')
    assert Identity.is_in(f'One id {id1} here')
    assert not Identity.is_in('No id here')


#
# def test_identity():
#     ids = [Identity._make_string() for x in range(3)]
#     assert len(ids) == 3
#     multiple_ids = 'some id {} another one {} and a last one {}'\
#                    .format(ids[0], ids[1], ids[2])
#     found_ids = Identity.find_all(multiple_ids)
#     assert len(found_ids) == 3
#     assert found_ids == ids
#
#     no_ids = 'asdf asdf asdf a  asdfkkjasd '
#     found_ids = Identity.find_all(no_ids)
#     assert type(found_ids) == list
#     assert len(found_ids) == 0