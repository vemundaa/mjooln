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
    assert list(tree.leaves()) == []


def test_grow(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_second_tree')
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    assert len(list(tree.leaves())) == num_files
    assert tree.total_weeds() == 0


def test_grow_compressed(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_second_tree', compress_all=True)
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    assert len(list(tree.leaves())) == num_files
    assert tree.total_weeds() == 0


def test_grow_encrypted(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_second_tree',
                         encrypt_all=True, crypt_key=mj.Crypt.generate_key())
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    assert len(list(tree.leaves())) == num_files
    assert tree.total_weeds() == 0


def test_reshape(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_third_tree')
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    leaves = tree.leaves()
    for leaf in leaves:
        assert not leaf.file().is_compressed()
    assert len(list(tree.leaves())) == num_files
    assert tree.total_weeds() == 0
    tree.reshape(compress_all=True)
    assert tree.total_weeds() == 0
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    for leaf in leaves:
        assert leaf.file().is_compressed()

    tree.reshape(compress_all=False)
    assert tree.total_weeds() == 0
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    for leaf in leaves:
        assert not leaf.file().is_compressed()

    # Test that tree cannot be encrypted if there was no encryption key added to tree class
    with pytest.raises(mj.LeafError):
        tree.reshape(encrypt_all=True)


def test_reshape_encrypted(ground, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(ground, 'my_second_tree',
                         encrypt_all=True, crypt_key=mj.Crypt.generate_key())
    for file in tmp_files:
        s = mj.Segment(key='just_for_test')
        tree.grow(file, s)

    assert len(list(tree.leaves())) == num_files
    assert tree.total_weeds() == 0
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    for leaf in leaves:
        assert not leaf.file().is_compressed()
        assert leaf.file().is_encrypted()

    tree.reshape(compress_all=True)
    assert tree.total_weeds() == 0
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    for leaf in leaves:
        assert leaf.file().is_compressed()
        assert leaf.file().is_encrypted()

    tree.reshape(compress_all=False)
    assert tree.total_weeds() == 0
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    for leaf in leaves:
        assert not leaf.file().is_compressed()
        assert leaf.file().is_encrypted()

    tree.reshape(compress_all=False, encrypt_all=False)
    assert tree.total_weeds() == 0
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    for leaf in leaves:
        assert not leaf.file().is_compressed()
        assert not leaf.file().is_encrypted()

    tree.reshape(compress_all=True, encrypt_all=True)
    assert tree.total_weeds() == 0
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    for leaf in leaves:
        assert leaf.file().is_compressed()
        assert leaf.file().is_encrypted()


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
    assert len(list(leaves)) == num_files
    assert tree.total_weeds() == 0
    assert len(tree._folder.list()) == num_files

    tree.reshape(key_level=2, date_level=3, time_level=3)
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    assert tree.total_weeds() == 0
    assert len(tree._folder.list()) == 1

    tree.reshape(key_level=0, date_level=0, time_level=0)
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    assert tree.total_weeds() == 0
    assert len(tree._folder.list()) == num_files

    tree.reshape(key_level=2, date_level=2, time_level=0)
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    assert tree.total_weeds() == 0
    assert len(tree._folder.list()) == 1

    tree.reshape(key_level=1, date_level=2, time_level=2)
    leaves = tree.leaves()
    assert len(list(leaves)) == num_files
    assert tree.total_weeds() == 0
    assert len(tree._folder.list()) == 1


def test_weed(ground, several_tmp_files, several_segments):
    num_files = len(several_tmp_files)
    assert len(ground.list()) == num_files
    tree = mj.Tree.plant(ground, 'my_fourth_tree',
                         crypt_key=mj.Crypt.generate_key(),
                         key_level=1, date_level=1, time_level=1)
    for file, segment in zip(several_tmp_files, several_segments):
        tree.grow(file, segment=segment, delete_source=False)

    # Check that the source files are still in root folder, and that there is a tree folder there
    assert len(ground.list()) == num_files + 1

    assert tree.total_weeds() == 0
    one_file = several_tmp_files[0]
    one_folder = list(tree.leaves())[0].file().folder()
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

    leaf = list(tree.leaves())[0]
    leaf.file().encrypt(tree._crypt_key)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 1
    assert weeds['encryption_mismatch'] == 1

    leaf = list(tree.leaves())[1]
    leaf.file().compress()
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 2
    assert weeds['encryption_mismatch'] == 1
    assert weeds['compression_mismatch'] == 1

    tree.reshape(encrypt_all=True, compress_all=True)
    assert tree.total_weeds() == 0

    leaf = list(tree.leaves())[0]
    file = leaf.file()
    file.decrypt(tree._crypt_key)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 1
    assert weeds['encryption_mismatch'] == 1

    leaf = list(tree.leaves())[1]
    file = leaf.file()
    file = file.decrypt(tree._crypt_key)
    file = file.decompress()
    _ = file.encrypt(tree._crypt_key)
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 2
    assert weeds['encryption_mismatch'] == 1
    assert weeds['compression_mismatch'] == 1

    leaf = list(tree.leaves())[2]
    file = leaf.file()
    file = file.decrypt(tree._crypt_key)
    _ = file.decompress()
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 4
    assert weeds['encryption_mismatch'] == 2
    assert weeds['compression_mismatch'] == 2





