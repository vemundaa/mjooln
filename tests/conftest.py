import pytest
import mjooln as mj
import random
import string
import pandas as pd
import numpy as np
import random


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


def dev_create_df(count=10, start=None):
    df = pd.DataFrame(index=mj.Zulu.range(n=count, start=start))
    df.index.name = 'zulu'
    df['one'] = np.random.rand(count)
    texts = [''.join(random.choices(string.ascii_lowercase, k=9)) + str(x) for x in range(count)]
    df['two'] = texts
    df['three'] = np.random.rand(count)
    return df


def dev_create_test_files(files, num_chars=1000):
    import random
    import string
    for file in files:
        text = ''.join(random.choices(string.ascii_uppercase + string.digits + '\n',
                                      k=num_chars))
        file.write(text)
    return files


def dev_create_test_csv_files(files):
    start = mj.Zulu(2020, 1, 1)
    delta = mj.Zulu.delta(hours=1)
    for file in files:
        n = random.randint(10,50)
        df = dev_create_df(count=n, start=start)
        df.to_csv(file)
        start = df.index.max() + delta
    return files


@pytest.fixture()
def dfs():
    dfs = []
    start = mj.Zulu(2020, 1, 1)
    delta = mj.Zulu.delta(hours=1)
    for i in range(10):
        n = random.randint(10, 50)
        df = dev_create_df(count=n, start=start)
        dfs.append(df)
        start = df.index.max() + delta
    yield dfs


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
def tmp_csv_files(tmp_folder):
    files = [mj.File.join(tmp_folder, f'test_{i}.csv') for i in range(3)]
    dev_create_test_csv_files(files)
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
