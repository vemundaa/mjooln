import pytest
import mjooln as mj


@pytest.fixture()
def ground(tmp_folder):
    yield mj.Ground.settle(tmp_folder)


def test_tree(tmp_folder):
    assert len(tmp_folder.list('*')) == 0
    tree = mj.Tree.plant(tmp_folder, 'my_first_tree')
    assert tree.key() == 'my_first_tree'
    assert len(tmp_folder.list()) == 1
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


def test_reshape(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_third_tree')
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    leaves = tree.leaves()
    for leaf in leaves:
        assert not leaf.is_compressed()
    assert len(tree.leaves()) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    tree.reshape(compress_all=True)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    leaves = tree.leaves()
    assert len(leaves) == num_files
    for leaf in leaves:
        assert leaf.is_compressed()

    tree.reshape(compress_all=False)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    leaves = tree.leaves()
    assert len(leaves) == num_files
    for leaf in leaves:
        assert not leaf.is_compressed()

    # Test that tree cannot be encrypted if there was no encryption key added to tree class
    with pytest.raises(mj.TreeError):
        tree.reshape(encrypt_all=True)


def test_reshape_encrypted(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_second_tree',
                         encrypt_all=True, encryption_key=mj.Crypt.generate_key())
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    assert len(tree.leaves()) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    leaves = tree.leaves()
    assert len(leaves) == num_files
    for leaf in leaves:
        assert not leaf.is_compressed()
        assert leaf.is_encrypted()

    tree.reshape(compress_all=True)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    leaves = tree.leaves()
    assert len(leaves) == num_files
    for leaf in leaves:
        assert leaf.is_compressed()
        assert leaf.is_encrypted()

    tree.reshape(compress_all=False)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    leaves = tree.leaves()
    assert len(leaves) == num_files
    for leaf in leaves:
        assert not leaf.is_compressed()
        assert leaf.is_encrypted()

    tree.reshape(compress_all=False, encrypt_all=False)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    leaves = tree.leaves()
    assert len(leaves) == num_files
    for leaf in leaves:
        assert not leaf.is_compressed()
        assert not leaf.is_encrypted()

    tree.reshape(compress_all=True, encrypt_all=True)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    leaves = tree.leaves()
    assert len(leaves) == num_files
    for leaf in leaves:
        assert leaf.is_compressed()
        assert leaf.is_encrypted()


def test_prune(error, ground, several_segment_files):
    num_files = len(several_segment_files)
    segment = mj.Segment(several_segment_files[0].stub())
    if not len(segment.key.parts()) > 1:
        raise error(f'This test requires minimum two parts in key: {segment.key}')
    assert len(ground.list()) == num_files
    tree = mj.Tree.plant(ground, 'my_second_tree')
    for file in several_segment_files:
        tree.grow(file, delete_source=True)

    # Test if source has been deleted
    assert len(ground.list()) == 1

    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == num_files

    tree.reshape(key_levels=2, date_levels=3, time_levels=3)
    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == 1

    tree.reshape(key_levels=0, date_levels=0, time_levels=0)
    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == num_files

    tree.reshape(key_levels=2, date_levels=2, time_levels=0)
    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == 1

    tree.reshape(key_levels=1, date_levels=2, time_levels=2)
    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == 1


def test_weed(ground, several_tmp_files, several_segments):
    num_files = len(several_tmp_files)
    assert len(ground.list()) == num_files
    tree = mj.Tree.plant(ground, 'my_fourth_tree',
                         encryption_key=mj.Crypt.generate_key(),
                         key_levels=1, date_levels=1, time_levels=1)
    for file, segment in zip(several_tmp_files, several_segments):
        tree.grow(file, segment=segment, delete_source=False)

    # Check that the source files are still in root folder, and that there is a tree folder there
    assert len(ground.list()) == num_files + 1

    assert tree.total_weeds() == 0
    one_file = several_tmp_files[0]
    one_folder = tree.leaves()[0].folder()
    one_file.copy(one_folder)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 1
    assert weeds['not_leaves'] == 1

    two_folder = one_folder.append('dumbass')
    two_folder.create()
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 2
    assert weeds['not_leaves'] == 1
    assert weeds['empty_folders'] == 1

    tree.prune()
    assert tree.total_weeds() == 0

    leaf = tree.leaves()[0]
    leaf.encrypt(tree._encryption_key)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 1
    assert weeds['encryption_mismatch'] == 1

    leaf = tree.leaves()[1]
    leaf.compress()
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 2
    assert weeds['encryption_mismatch'] == 1
    assert weeds['compression_mismatch'] == 1

    tree.reshape(encrypt_all=True, compress_all=True)
    assert tree.total_weeds() == 0

    leaf = tree.leaves()[0]
    leaf.decrypt(tree._encryption_key)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 1
    assert weeds['encryption_mismatch'] == 1

    leaf = tree.leaves()[1]
    leaf = leaf.decrypt(tree._encryption_key)
    leaf = leaf.decompress()
    _ = leaf.encrypt(tree._encryption_key)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 2
    assert weeds['encryption_mismatch'] == 1
    assert weeds['compression_mismatch'] == 1

    leaf = tree.leaves()[2]
    leaf = leaf.decrypt(tree._encryption_key)
    _ = leaf.decompress()
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 4
    assert weeds['encryption_mismatch'] == 2
    assert weeds['compression_mismatch'] == 2





