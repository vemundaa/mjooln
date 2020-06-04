import pytest
import os
import mjooln as mj

_num_items = 3

# TODO: Add check for is_empty, is_null and delete, with exceptions


def _make(folder, subfolder, name, is_folder, exists):
    paths = []
    for i in range(_num_items):
        if subfolder:
            folder = os.path.join(folder, subfolder)
        else:
            folder = folder
        path = os.path.join(folder, name.format(i))
        if exists and is_folder:
            if not os.path.exists(path):
                os.makedirs(path)
        if exists and not is_folder:
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(path, 'w') as f:
                f.write('Some simple text')
        paths.append(mj.Path(path))
    return paths


@pytest.fixture()
def paths(tmp_folder):
    paths = {}
    paths['files'] = _make(tmp_folder, '', 'file_{}.txt', False, True)
    paths['not_files'] = _make(tmp_folder, '', 'not_file_{}.txt', False, False)
    paths['folders'] = _make(tmp_folder, '', 'folder_{}', True, True)
    paths['not_folders'] = _make(tmp_folder, '', 'not_folder_{}', True, False)
    subfolder = paths['folders'][0]
    for i in range(_num_items):
        paths['files_in_folder'] = _make(tmp_folder, subfolder, 'file_in_folder_{}.txt', False, True)
        paths['not_files_in_folder'] = _make(tmp_folder, subfolder, 'not_file_in_folder_{}.txt', False, False)
        paths['folders_in_folder'] = _make(tmp_folder, subfolder, 'folder_in_folder_{}', True, True)
        paths['not_folders_in_folder'] = _make(tmp_folder, subfolder, 'not_folder_in_folder_{}', True, False)

    yield paths


def test_slashes():
    assert mj.Path('/') == '/'
    assert mj.Path('\\') == '/'
    if mj.Path.platform() == mj.Path._WINDOWS:
        assert mj.Path('C:\\dev\\dummy') == 'C:/dev/dummy'
        assert mj.Path('C:/dev\\dummy') == 'C:/dev/dummy'
    else:
        assert mj.Path('\\dev\\dummy') == '/dev/dummy'
        assert mj.Path('/dev\\dummy') == '/dev/dummy'


def test_drives():
    if mj.Path.platform() == mj.Path._WINDOWS:
        assert mj.Path('C:/dev/dummy').mountpoint() == 'C:'
    else:
        with pytest.raises(mj.PathError):
            mj.Path('C:/dev/dummy')
    # TODO: Add these tests if changing drive handling
    # assert mj.Path('/dev/dummy').drive() == ''
    # assert mj.Path('dev/dummy').drive() == ''


def test_parts():
    if mj.Path.platform() == mj.Path._WINDOWS:
        assert mj.Path('C:/dev/dummy').parts() == ['C:', 'dev', 'dummy']
    assert mj.Path('/how/to/do/this').parts() == ['how', 'to', 'do', 'this']
    assert mj.Path('/and\\odd/slashes').parts() == ['and', 'odd', 'slashes']


# def test_ending():
#     assert mj.Path('def.txt').endings() == ['txt']
#     assert mj.Path('/help/me/something.txt.gz').endings() == ['txt', 'gz']


# def test_clean(mj.Paths):
#     assert len(glob.glob(os.mj.Path.join(cfg.TESTDIR, '*'))) > 0
#     mj.Path(cfg.TESTDIR).empty()
#     assert len(glob.glob(os.mj.Path.join(cfg.TESTDIR, '*'))) == 0


def test_exists_and_is_type(paths):
    for f in paths['not_files']:
        p = mj.Path(f)
        assert not p.exists()
        with pytest.raises(mj.PathError):
            p.is_file()
        with pytest.raises(mj.PathError):
            p.is_folder()

    for f in paths['not_folders']:
        p = mj.Path(f)
        assert not p.exists()
        with pytest.raises(mj.PathError):
            p.is_file()
        with pytest.raises(mj.PathError):
            p.is_folder()

    for f in paths['files']:
        p = mj.Path(f)
        assert p.exists()
        assert p.is_file()
        assert not p.is_folder()

    for f in paths['folders']:
        p = mj.Path(f)
        assert p.exists()
        assert not p.is_file()
        assert p.is_folder()

    for f in paths['not_files_in_folder']:
        p = mj.Path(f)
        assert not p.exists()
        with pytest.raises(mj.PathError):
            p.is_file()
        with pytest.raises(mj.PathError):
            p.is_folder()

    for f in paths['not_folders_in_folder']:
        p = mj.Path(f)
        assert not p.exists()
        with pytest.raises(mj.PathError):
            p.is_file()
        with pytest.raises(mj.PathError):
            p.is_folder()

    for f in paths['files_in_folder']:
        p = mj.Path(f)
        assert p.exists()
        assert p.is_file()
        assert not p.is_folder()

    for f in paths['folders_in_folder']:
        p = mj.Path(f)
        assert p.exists()
        assert not p.is_file()
        assert p.is_folder()


def test_list(tmp_folder, paths):
    path_list = []
    for key in paths:
        path_list += paths[key]

    check_paths = [mj.Path(x) for x in path_list]
    check_paths = [str(x) for x in check_paths if x.exists()]
    list_paths = mj.Path(tmp_folder).list('*', recursive=True)
    assert set(list_paths) == set(check_paths)

    check_paths = [mj.Path(x) for x in path_list if x.endswith('.txt')]
    check_paths = [str(x) for x in check_paths if x.exists()]
    list_paths = mj.Path(tmp_folder).list('*.txt', recursive=True)
    assert set(list_paths) == set(check_paths)

    path_list = paths['files'] + paths['folders']
    check_paths = [mj.Path(x) for x in path_list]
    check_paths = [str(x) for x in check_paths if x.exists()]
    list_paths = mj.Path(tmp_folder).list('*')
    assert set(check_paths) == set(list_paths)

    check_paths = [x for x in check_paths if x.endswith('.txt')]
    list_paths = mj.Path(tmp_folder).list('*.txt')
    assert set(check_paths) == set(list_paths)







