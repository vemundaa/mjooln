
def test_encrypt(tmp_files):
    tmp_dir = cfg.TESTDIR
    assert len(tmp_dir.list('*.txt')) == _num_test_files

    tmp_file = tmp_files[0]
    data_before = tmp_file.read()
    extension = tmp_file.extension()
    assert extension == 'txt'
    assert not tmp_file.is_encrypted()
    key = AES.generate_key()
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
    salt = AES.salt()
    key = AES.key_from_password(salt, 'test')
    efile = tmp_file.encrypt(key)
    assert efile.extension() == 'txt'
    assert efile.is_encrypted()

    key = AES.key_from_password(salt, 'test')
    dfile = efile.decrypt(key)
    assert not dfile.is_compressed()
    assert dfile.extension() == 'txt'
    data_after = dfile.read()
    assert data_before == data_after



