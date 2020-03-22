import pytest

from mjooln import Crypt, TextFile, TextFileError, FileError


def test_text_file(tmp_folder):
    file = TextFile.join(tmp_folder, 'test.txt')
    text = 'Here is some text.'
    file.write(text)
    assert file.read() == text
    compressed_file = file.compress()
    assert compressed_file.read() == text
    crypt_key = Crypt.generate_key()
    encrypted_file = compressed_file.encrypt(crypt_key=crypt_key)
    assert encrypted_file.read(crypt_key=crypt_key) == text


def test_encryption_mismatch(tmp_folder):
    file = TextFile.join(tmp_folder, 'test.txt')
    text = 'Here is some text.'
    with pytest.raises(FileError):
        file.write(text, password='dummy')


def test_text_file_append(tmp_folder):
    file = TextFile.join(tmp_folder, 'test.txt')
    text = 'Here is some text.'
    more_text = ' And some more.'
    file.write(text)
    file.append(more_text)
    assert file.read() == text + more_text

    file.write(text)
    compressed_file = file.compress()
    compressed_file.append(more_text)
    assert compressed_file.read() == text + more_text

    file.write(text)
    crypt_key = Crypt.generate_key()
    encrypted_file = file.encrypt(crypt_key=crypt_key)
    encrypted_file.append(more_text, crypt_key=crypt_key)
    assert encrypted_file.read(crypt_key=crypt_key) == text + more_text

    file.write(text)
    file = file.compress()
    crypt_key = Crypt.generate_key()
    encrypted_file = file.encrypt(crypt_key=crypt_key)
    encrypted_file.append(more_text, crypt_key=crypt_key)
    assert encrypted_file.read(crypt_key=crypt_key) == text + more_text

