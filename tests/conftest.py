import pytest
import mjooln as mj
import random
import string


@pytest.fixture()
def error():
    class TestError(Exception):
        pass
    return TestError

@pytest.fixture()
def random_string(num_chars=1000):
    yield ''.join(random.choices(string.ascii_uppercase + string.digits + '\n',
                                 k=num_chars))


@pytest.fixture()
def dic():
    return {
        'zulu': mj.Zulu(),
        'text': 'Some very good text',
        'number': 34,
        'float': 3333.3333,
    }


def dev_create_test_files(files, num_chars=1000):
    import random
    import string
    for file in files:
        text = ''.join(random.choices(string.ascii_uppercase + string.digits + '\n',
                                      k=num_chars))
        file.write(text)
    return files


@pytest.fixture()
def tmp_folder():
    folder = mj.Folder.home().append('.mjooln_tmp_test_2SgTkk')
    folder.touch()
    folder.empty()
    yield folder
    folder.empty()
    folder.remove()


@pytest.fixture()
def tmp_files(tmp_folder):
    files = [mj.File.join(tmp_folder, f'test_{i}.txt') for i in range(3)]
    dev_create_test_files(files)
    yield files
    for file in files:
        file.delete(missing_ok=True)


@pytest.fixture()
def several_tmp_files(tmp_folder):
    files = [mj.File.join(tmp_folder, f'test_{i}.txt') for i in range(30)]
    dev_create_test_files(files)
    yield files
    for file in files:
        file.delete(missing_ok=True)


@pytest.fixture()
def several_segments():
    zulus = mj.Zulu.range(n=30)
    return [mj.Segment(key='test_files__lots', zulu=x) for x in zulus]


@pytest.fixture()
def several_segment_files(tmp_folder):
    zulus = mj.Zulu.range(n=30)
    segments = [mj.Segment(key='test_files__lots', zulu=x) for x in zulus]
    files = [mj.File.join(tmp_folder, f'{s}.txt') for s in segments]
    dev_create_test_files(files)
    yield files
    for file in files:
        file.delete(missing_ok=True)
