import pytest
import mjooln as mj


@pytest.fixture()
def ground(tmp_folder):
    yield mj.Ground.settle(tmp_folder)


def test_tree(ground):
    assert len(ground.list('.*')) == 1
    tree = mj.Tree.plant(ground, 'my_first_tree')
    assert tree._key == 'my_first_tree'
    assert len(ground.list()) == 1
    assert tree._folder.list() == []
    assert tree.leaves() == []


def test_grow(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_second_tree')
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    assert len(tree.leaves()) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0


def test_grow_compressed(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_second_tree', compress_all=True)
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    assert len(tree.leaves()) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0


def test_grow_encrypted(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_second_tree',
                         encrypt_all=True, encryption_key=mj.Crypt.generate_key())
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    assert len(tree.leaves()) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0

