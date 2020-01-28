import pytest

from mjooln import Config
from mjooln import File, FileError, Folder, FolderError, Volume, VolumeError

cfg = Config.get()

_num_test_files = 3


def dev_create_test_files(files, num_chars=1000):
    import random
    import string
    for file in files:
        text = ''.join(random.choices(string.ascii_uppercase + string.digits + '\n',
                                      k=num_chars))
        file.write(text)
    return files


@pytest.fixture()
def tmp_files():
    cfg.TESTDIR.empty()
    files = [File.join(cfg.TESTDIR, f'test_{i}.txt') for i in range(3)]
    dev_create_test_files(files)
    yield files
    for file in files:
        file.delete(missing_ok=True)


def test_volume():
    Volume('/')
    with pytest.raises(VolumeError):
        Volume(cfg.TESTDIR)


def test_folder(tmp_files):
    with pytest.raises(FolderError):
        Folder(str(tmp_files[0]))
    with pytest.raises(FolderError):
        Folder('/')
    folder = Folder.join(cfg.TESTDIR, 'new_folder')
    assert len(cfg.TESTDIR.list()) == _num_test_files
    folder.create()
    assert len(list(folder.list())) == 0
    assert len(cfg.TESTDIR.list()) == _num_test_files + 1
    folder.remove()
    assert len(cfg.TESTDIR.list()) == _num_test_files


def test_file_error():
    folder = cfg.TESTDIR.append('new_folder')
    folder.create()
    with pytest.raises(FileError):
        File(str(folder))
    file = File.join(cfg.TESTDIR, 'somefile.txt')
    assert file == File(file)
    assert file == File.elf(file)
    assert file == file.elf(file)


def test_volume_error():
    cfg.TESTDIR.empty()
    assert cfg.TESTDIR.is_empty()
    folder = cfg.TESTDIR.append('new_folder')
    folder.create()
    assert len(cfg.TESTDIR.list()) == 1
    with pytest.raises(VolumeError):
        Volume(str(folder))
    folder.remove()
    assert cfg.TESTDIR.is_empty()


def test_delete(tmp_files):
    path_list = cfg.TESTDIR.list()
    num_files = len(path_list)
    for path in path_list:
        path = File(path)
        if path.exists() and path.is_file():
            path.delete()
            num_files -= 1
        assert len(cfg.TESTDIR.list()) == num_files
    # folders = [Folder(x) for x in paths['folders']]
    # assert not folders[0].is_empty()
    # with pytest.raises(PathError):
    #     folders[0].delete()
    # folders[0].empty()
    # for folder in folders:
    #     assert folder.is_empty()
    #     folder.delete()
    #     num_files -= 1
    #     assert len(Path(cfg.TESTDIR).list()) == num_files


def test_hidden():
    f = File('.something_hidden')
    assert f.is_hidden()


def test_stub():
    stub = 'something'
    variations = [
        stub,
        '.' + stub,
        stub + '.txt',
        stub + '.txt.gz',
        '.' + stub + '.txt',
        '.' + stub + '.txt.gz'
    ]
    for v in variations:
        f = File(v)
        assert f.stub() == stub


def test_compression(tmp_files):
    tmp_dir = cfg.TESTDIR
    assert len(tmp_dir.list('*.txt')) == _num_test_files

    tmp_file = tmp_files[0]
    size_before = tmp_file.size()
    extension_before = tmp_file.extension()
    assert extension_before == 'txt'
    assert not tmp_file.is_compressed()
    tmp_file = tmp_file.compress()
    assert len(tmp_dir.list('*.txt')) == _num_test_files - 1
    assert len(tmp_dir.list('*.txt.gz')) == 1
    size_after = tmp_file.size()
    assert tmp_file.is_compressed()
    assert size_after < size_before
    assert tmp_file.extension() == 'txt'
    tmp_file = tmp_file.decompress()
    assert not tmp_file.is_compressed()
    assert tmp_file.size() == size_before
    assert tmp_file.extension() == 'txt'

    assert len(tmp_dir.list('*.txt')) == _num_test_files


def test_copy(tmp_files):
    source_folder = cfg.TESTDIR
    assert len(source_folder.list('*.txt')) == _num_test_files
    copy_folder = cfg.TESTDIR.append('copy')
    copy_folder.create()
    copied = []
    for tmp_file in tmp_files[1:]:
        with pytest.raises(FileError):
            tmp_file.copy(cfg.TESTDIR)
        copy_file = tmp_file.copy(copy_folder)
        copied.append(copy_file)
    assert len(source_folder.list('*.txt')) == _num_test_files
    assert len(copy_folder.list('*.txt')) == _num_test_files - 1
    for file in tmp_files:
        file.delete()
    assert len(source_folder.list('*.txt')) == 0
    assert len(copy_folder.list('*.txt')) == _num_test_files - 1
    for file in copied:
        file.delete()
    assert len(source_folder.list('*.txt')) == 0
    assert len(copy_folder.list('*.txt')) == 0


def test_move(tmp_files):
    source_dir = cfg.TESTDIR
    move_dir = cfg.TESTDIR.append('move')
    assert len(source_dir.list('*.txt')) == _num_test_files
    moved = []
    for tmp_file in tmp_files[1:]:
        moved_file = tmp_file.move(move_dir)
        moved.append(moved_file)
    assert len(source_dir.list('*.txt')) == 1
    assert len(move_dir.list('*.txt')) == _num_test_files - 1
    for moved_file in moved:
        _ = moved_file.move(source_dir)
    assert len(source_dir.list('*.txt')) == _num_test_files
    assert len(source_dir.list('*.txt.move')) == 0


def test_encrypt(tmp_files):
    tmp_dir = cfg.TESTDIR
    assert len(tmp_dir.list('*.txt')) == _num_test_files

    tmp_file = tmp_files[0]
    data_before = tmp_file.read()
    extension = tmp_file.extension()
    assert extension == 'txt'
    assert not tmp_file.is_encrypted()
    key = tmp_file.generate_key()
    efile = tmp_file.encrypt(key)
    assert efile.extension() == 'txt'
    assert efile.is_encrypted()

    dfile = efile.decrypt(key)
    assert not dfile.is_compressed()
    assert dfile.extension() == 'txt'
    data_after = dfile.read()
    assert data_before == data_after

    tmp_file = tmp_files[1]
    data_before = tmp_file.read()
    extension = tmp_file.extension()
    assert extension == 'txt'
    assert not tmp_file.is_encrypted()
    salt = File.salt()
    key = File.key_from_password(salt, 'test')
    efile = tmp_file.encrypt(key)
    assert efile.extension() == 'txt'
    assert efile.is_encrypted()

    key = File.key_from_password(salt, 'test')
    dfile = efile.decrypt(key)
    assert not dfile.is_compressed()
    assert dfile.extension() == 'txt'
    data_after = dfile.read()
    assert data_before == data_after




