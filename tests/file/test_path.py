import pytest
import os
import shutil

from tests.config import Config
from mjooln import Path, PathError

cfg = Config.get()

_num_items = 3

# TODO: Add check for is_empty, is_null and delete, with exceptions


def _make(subfolder, name, is_folder, exists):
    paths = []
    for i in range(_num_items):
        if subfolder:
            folder = os.path.join(cfg.TESTDIR, subfolder)
        else:
            folder = cfg.TESTDIR
        path = os.path.join(folder, name.format(i))
        if exists and is_folder:
            if not os.path.exists(path):
                os.makedirs(path)
        if exists and not is_folder:
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(path, 'w') as f:
                f.write('Some simple text')
        paths.append(path)
    return paths


@pytest.fixture()
def paths():
    paths = {}
    paths['files'] = _make('','file_{}.txt', False, True)
    paths['not_files'] = _make('', 'not_file_{}.txt', False, False)
    paths['folders'] = _make('', 'folder_{}', True, True)
    paths['not_folders'] = _make('', 'not_folder_{}', True, False)
    subfolder = paths['folders'][0]
    for i in range(_num_items):
        paths['files_in_folder'] = _make(subfolder, 'file_in_folder_{}.txt', False, True)
        paths['not_files_in_folder'] = _make(subfolder, 'not_file_in_folder_{}.txt', False, False)
        paths['folders_in_folder'] = _make(subfolder, 'folder_in_folder_{}', True, True)
        paths['not_folders_in_folder'] = _make(subfolder, 'not_folder_in_folder_{}', True, False)

    yield paths
    shutil.rmtree(cfg.TESTDIR)
    os.makedirs(cfg.TESTDIR)


def test_slashes():
    assert Path('/') == '/'
    assert Path('\\') == '/'
    if Path.platform() == Path.WINDOWS:
        assert Path('C:\\dev\\dummy') == 'C:/dev/dummy'
        assert Path('C:/dev\\dummy') == 'C:/dev/dummy'
    else:
        assert Path('\\dev\\dummy') == '/dev/dummy'
        assert Path('/dev\\dummy') == '/dev/dummy'


def test_drives():
    if Path.platform() == Path.WINDOWS:
        assert Path('C:/dev/dummy').mountpoint() == 'C:'
    else:
        with pytest.raises(PathError):
            Path('C:/dev/dummy')
    # TODO: Add these tests if changing drive handling
    # assert Path('/dev/dummy').drive() == ''
    # assert Path('dev/dummy').drive() == ''


def test_parts():
    if Path.platform() == Path.WINDOWS:
        assert Path('C:/dev/dummy').parts() == ['C:', 'dev', 'dummy']
    assert Path('/how/to/do/this').parts() == ['how', 'to', 'do', 'this']
    assert Path('/and\\odd/slashes').parts() == ['and', 'odd', 'slashes']


# def test_ending():
#     assert Path('def.txt').endings() == ['txt']
#     assert Path('/help/me/something.txt.gz').endings() == ['txt', 'gz']


# def test_clean(paths):
#     assert len(glob.glob(os.path.join(cfg.TESTDIR, '*'))) > 0
#     Path(cfg.TESTDIR).empty()
#     assert len(glob.glob(os.path.join(cfg.TESTDIR, '*'))) == 0


def test_exists_and_is_type(paths):
    for f in paths['not_files']:
        p = Path(f)
        assert not p.exists()
        with pytest.raises(PathError):
            p.is_file()
        with pytest.raises(PathError):
            p.is_folder()

    for f in paths['not_folders']:
        p = Path(f)
        assert not p.exists()
        with pytest.raises(PathError):
            p.is_file()
        with pytest.raises(PathError):
            p.is_folder()

    for f in paths['files']:
        p = Path(f)
        assert p.exists()
        assert p.is_file()
        assert not p.is_folder()

    for f in paths['folders']:
        p = Path(f)
        assert p.exists()
        assert not p.is_file()
        assert p.is_folder()

    for f in paths['not_files_in_folder']:
        p = Path(f)
        assert not p.exists()
        with pytest.raises(PathError):
            p.is_file()
        with pytest.raises(PathError):
            p.is_folder()

    for f in paths['not_folders_in_folder']:
        p = Path(f)
        assert not p.exists()
        with pytest.raises(PathError):
            p.is_file()
        with pytest.raises(PathError):
            p.is_folder()

    for f in paths['files_in_folder']:
        p = Path(f)
        assert p.exists()
        assert p.is_file()
        assert not p.is_folder()

    for f in paths['folders_in_folder']:
        p = Path(f)
        assert p.exists()
        assert not p.is_file()
        assert p.is_folder()


def test_list(paths):
    path_list = []
    for key in paths:
        path_list += paths[key]

    check_paths = [Path(x) for x in path_list]
    check_paths = [str(x) for x in check_paths if x.exists()]
    list_paths = Path(cfg.TESTDIR).list('*', recursive=True)
    assert set(list_paths) == set(check_paths)

    check_paths = [Path(x) for x in path_list if x.endswith('.txt')]
    check_paths = [str(x) for x in check_paths if x.exists()]
    list_paths = Path(cfg.TESTDIR).list('*.txt', recursive=True)
    assert set(list_paths) == set(check_paths)

    path_list = paths['files'] + paths['folders']
    check_paths = [Path(x) for x in path_list]
    check_paths = [str(x) for x in check_paths if x.exists()]
    list_paths = Path(cfg.TESTDIR).list('*')
    assert set(check_paths) == set(list_paths)

    check_paths = [x for x in check_paths if x.endswith('.txt')]
    list_paths = Path(cfg.TESTDIR).list('*.txt')
    assert set(check_paths) == set(list_paths)







