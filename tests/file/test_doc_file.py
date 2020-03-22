import mjooln as mj


def test_doc_file(tmp_folder):
    class Sample(mj.DocFile):

        def __init__(self, file_path):
            # First define the variables, and their default values
            self.some_data = 'default string'
            self.some_number = 0.3

            # Then, init the super class (which will load from file if exists)
            super().__init__(file_path)

    file_path = mj.File.join(tmp_folder, 'dummy.json')
    assert len(tmp_folder.list()) == 0
    s = Sample(file_path)
    # File should have been created now
    assert len(tmp_folder.list()) == 1
    default_dic = s.dic()
    s.some_data = 'new string'
    s.some_number = 1.3

    ss = Sample(file_path)
    assert ss.dic() == default_dic
    s.write()
    ss.read()
    assert s.dic() == ss.dic()


def test_doc_file_compressed(tmp_folder):
    class Sample(mj.DocFile):

        def __init__(self, file_path):
            # First define the variables, and their default values
            self.some_data = 'default string'
            self.some_number = 0.3

            # Then, init the super class (which will load from file if exists)
            super().__init__(file_path)

    file_path = mj.File.join(tmp_folder, 'dummy.json.gz')
    assert len(tmp_folder.list()) == 0
    s = Sample(file_path)
    # File should have been created now
    assert len(tmp_folder.list()) == 1
    default_dic = s.dic()
    s.some_data = 'new string'
    s.some_number = 1.3

    ss = Sample(file_path)
    assert ss.dic() == default_dic
    s.write()
    ss.read()
    assert s.dic() == ss.dic()


def test_doc_file_compressed_encrypted(tmp_folder):
    class Sample(mj.DocFile):

        def __init__(self, file_path):
            # First define the variables, and their default values
            self.some_data = 'default string'
            self.some_number = 0.3

            # Then, init the super class (which will load from file if exists)
            super().__init__(file_path,  password='dummy')

    file_path = mj.File.join(tmp_folder, 'dummy.json.gz.aes')
    assert len(tmp_folder.list()) == 0
    s = Sample(file_path)
    # File should have been created now
    assert len(tmp_folder.list()) == 1
    default_dic = s.dic()
    s.some_data = 'new string'
    s.some_number = 1.3

    ss = Sample(file_path)
    assert ss.dic() == default_dic
    s.write()
    ss.read()
    assert s.dic() == ss.dic()
