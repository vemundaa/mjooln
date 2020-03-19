import pytest
import mjooln as mj


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
def dic():
    return {
        'zulu': mj.Zulu(),
        'text': 'Some very good text',
        'number': 34,
        'float': 3333.3333,
    }
