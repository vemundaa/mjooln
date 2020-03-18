import pytest
import mjooln as mj


def test_volume():
    assert mj.Path('/').is_volume()


def test_folder(tmp_folder, tmp_files):
    _num_test_files = len(tmp_files)
    with pytest.raises(mj.FolderError):
        mj.Folder(str(tmp_files[0]))
    with pytest.raises(mj.FolderError):
        mj.Folder('/')
    folder = mj.Folder.join(tmp_folder, 'new_folder')
    assert len(tmp_folder.list()) == _num_test_files
    folder.create()
    assert len(folder.list()) == 0
    assert len(tmp_folder.list()) == _num_test_files + 1
    assert len(tmp_folder.files()) == _num_test_files
    assert len(tmp_folder.folders()) == 1
    folder.remove()
    assert len(tmp_folder.list()) == _num_test_files
    assert len(tmp_folder.files()) == _num_test_files
    assert len(tmp_folder.folders()) == 0


def test_file_error(tmp_folder):
    folder = tmp_folder.append('new_folder')
    folder.create()
    with pytest.raises(mj.FileError):
        mj.File(str(folder))
    file = mj.File.join(folder, 'somefile.txt')
    assert file == mj.File(file)
    assert file == mj.File.elf(file)
    assert file == file.elf(file)


def test_create_folder(tmp_folder):
    assert tmp_folder.is_empty()
    folder = tmp_folder.append('new_folder')
    folder.create()
    assert len(tmp_folder.list()) == 1
    folder.remove()
    assert tmp_folder.is_empty()


def test_delete(tmp_folder, tmp_files):
    path_list = tmp_folder.list()
    num_files = len(path_list)
    for path in path_list:
        path = mj.File(path)
        if path.exists() and path.is_file():
            path.delete()
            num_files -= 1
        assert len(tmp_folder.list()) == num_files


def test_hidden():
    f = mj.File('.something_hidden')
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
        f = mj.File(v)
        assert f.stub() == stub


def test_compression(tmp_folder, tmp_files):
    _num_test_files = len(tmp_files)
    assert len(tmp_folder.list('*.txt')) == _num_test_files
    tmp_file = tmp_files[0]
    size_before = tmp_file.size()
    extension_before = tmp_file.extension()
    assert extension_before == 'txt'
    assert not tmp_file.is_compressed()
    tmp_file = tmp_file.compress()
    assert len(tmp_folder.list('*.txt')) == _num_test_files - 1
    assert len(tmp_folder.list('*.txt.gz')) == 1
    size_after = tmp_file.size()
    assert tmp_file.is_compressed()
    assert size_after < size_before
    assert tmp_file.extension() == 'txt'
    tmp_file = tmp_file.decompress()
    assert not tmp_file.is_compressed()
    assert tmp_file.size() == size_before
    assert tmp_file.extension() == 'txt'

    assert len(tmp_folder.list('*.txt')) == _num_test_files


def test_copy(tmp_folder, tmp_files):
    _num_test_files = len(tmp_files)
    source_folder = tmp_folder
    assert len(source_folder.list('*.txt')) == _num_test_files
    copy_folder = tmp_folder.append('copy')
    copy_folder.create()
    copied = []
    for tmp_file in tmp_files[1:]:
        with pytest.raises(mj.FileError):
            tmp_file.copy(tmp_folder)
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


def test_move(tmp_folder, tmp_files):
    _num_test_files = len(tmp_files)
    source_dir = tmp_folder
    move_dir = tmp_folder.append('move')
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

