import pytest
import mjooln as mj


def test_tree(tmp_folder):
    assert len(tmp_folder.list('*')) == 0
    tree = mj.Tree.plant(tmp_folder, 'my_first_tree')
    assert tree.key() == 'my_first_tree'
    assert len(tmp_folder.list()) == 1
    assert tree._folder.list() == []
    assert tree.leaves() == []


def test_grow(tmp_folder, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(tmp_folder, 'my_second_tree')
    for file in tmp_files:
        s = mj.Atom(key='just_for_test')
        tree.grow(file, s)

    assert len(tree.leaves()) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0


def test_grow_compressed(tmp_folder, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(tmp_folder, 'my_second_tree', compress_all=True)
    for file in tmp_files:
        s = mj.Atom(key='just_for_test')
        tree.grow(file, s)

    assert len(tree.leaves()) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0


def test_grow_encrypted(tmp_folder, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(tmp_folder, 'my_second_tree',
                         encrypt_all=True, encryption_key=mj.Crypt.generate_key())
    for file in tmp_files:
        s = mj.Atom(key='just_for_test')
        tree.grow(file, s)

    assert len(tree.leaves()) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0


def test_reshape(tmp_folder, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(tmp_folder, 'my_third_tree')
    for file in tmp_files:
        s = mj.Atom(key='just_for_test')
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


def test_reshape_encrypted(tmp_folder, tmp_files):
    num_files = len(tmp_files)
    tree = mj.Tree.plant(tmp_folder, 'my_second_tree',
                         encrypt_all=True, encryption_key=mj.Crypt.generate_key())
    for file in tmp_files:
        s = mj.Atom(key='just_for_test')
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


def test_prune(error, tmp_folder, several_atom_files):
    # TODO: Add negative levels, and None, and 0 to double check.
    num_files = len(several_atom_files)
    atom = mj.Atom(several_atom_files[0].stub())
    if not len(atom.key.parts()) > 1:
        raise error(f'This test requires minimum two parts in key: {atom.key}')
    assert len(tmp_folder.list()) == num_files
    tree = mj.Tree.plant(tmp_folder, 'my_second_tree')
    for file in several_atom_files:
        tree.grow(file, delete_native=True)

    # Test if source has been deleted
    assert len(tmp_folder.list()) == 1

    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == 1

    tree.reshape(key_level=0, date_level=0, time_level=0)
    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == num_files

    tree.reshape(key_level=2, date_level=3, time_level=3)
    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == 1

    tree.reshape(key_level=0, date_level=0, time_level=0)
    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == num_files

    tree.reshape(key_level=2, date_level=2, time_level=0)
    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == 1

    tree.reshape(key_level=1, date_level=2, time_level=2)
    leaves = tree.leaves()
    assert len(leaves) == num_files
    weeds = tree.weeds()
    assert weeds['total_weeds'] == 0
    assert len(tree._folder.list()) == 1


def test_weed(tmp_folder, several_tmp_files, several_atoms):
    num_files = len(several_tmp_files)
    assert len(tmp_folder.list()) == num_files
    tree = mj.Tree.plant(tmp_folder, 'my_fourth_tree',
                         encryption_key=mj.Crypt.generate_key(),
                         key_level=1, date_level=1, time_level=1)
    for file, atom in zip(several_tmp_files, several_atoms):
        tree.grow(file, atom=atom, delete_native=False)

    # Check that the source files are still in root folder, and that there
    # is a tree folder there
    assert len(tmp_folder.list()) == num_files + 1

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

    tree.prune(delete_not_leaf=True)
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





