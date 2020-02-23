from mjooln.path.file import File
from mjooln.crypt.crypt import AES


class CryptFile(File):

    def write(self, content, mode='w'):


    def encrypt(self, key, delete_original=True):
        if not self.exists():
            raise FileError(f'Cannot encrypt non existent file: {self}')
        if self.is_encrypted():
            raise FileError(f'File is already encrypted: {self}')
        logger.debug(f'Encrypt file: {self}')
        encrypted_file = File(self + '.' + self.ENCRYPTED_EXTENSION)
        data = self.read(mode='rb')
        encrypted = AES.encrypt(data, key)
        encrypted_file.write(encrypted, mode='wb')
        if delete_original:
            self.delete()
        return encrypted_file

    def decrypt(self, key, delete_original=True):
        if not self.exists():
            raise FileError(f'Cannot decrypt non existent file: {self}')
        if not self.is_encrypted():
            raise FileError(f'File is already encrypted: {self}')

        logger.debug(f'Decrypt file: {self}')
        decrypted_file = File(self.replace('.' + self.ENCRYPTED_EXTENSION, ''))
        data = self.read(mode='rb')
        decrypted = AES.decrypt(data, key)
        decrypted_file.write(decrypted, mode='wb')
        if delete_original:
            self.delete()
        return decrypted_file