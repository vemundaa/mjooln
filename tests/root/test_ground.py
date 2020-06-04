import pytest
import mjooln as mj


def test_ground(tmp_folder):
    ground = mj.Field.settle(tmp_folder)
    assert ground.list() == []
    assert ground.roots() == []
    one_root = mj.Root.plant(ground, 'one_root')
    assert len(ground.roots()) == 1
    _ = mj.Root.plant(ground, 'two_root')
    assert len(ground.roots()) == 2
    assert len(ground.list()) == 2
    _ = mj.Root.plant(ground, 'three_root')
    assert len(ground.roots()) == 3
    assert len(ground.list()) == 3
    file = mj.File.join(tmp_folder, 'test.txt')
    file.write('nothing')
    assert len(ground.roots()) == 3
    assert len(ground.list()) == 4
    dic1 = one_root.dic()
    one_root = ground.root('one_root')
    assert one_root.dic() == dic1

    with pytest.raises(mj.FieldError):
        mj.Field.settle(tmp_folder)
