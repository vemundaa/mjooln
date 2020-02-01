import os
import base64
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptError(Exception):
    pass


class Crypt:

    @classmethod
    def generate_key(cls):
        return Fernet.generate_key()

    @classmethod
    def salt(cls):
        return os.urandom(16)

    @classmethod
    def key_from_password(cls, salt, password):
        password = password.encode()  # Convert to type bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password))


class AES(Crypt):

    @classmethod
    def encrypt(cls, data, key):
        if not type(data) == bytes:
            raise CryptError('Cannot encrypt data. Data is not bytes')
        if not type(key) == bytes:
            raise CryptError('Cannot encrypt data. Key is not bytes')
        fernet = Fernet(key)
        return fernet.encrypt(data)

    @classmethod
    def decrypt(cls, data, key):
        # TODO: Catch InvalidToken error
        if not type(data) == bytes:
            raise CryptError('Cannot encrypt data. Data is not bytes')
        if not type(key) == bytes:
            raise CryptError('Cannot decrypt data. Key is not bytes')
        fernet = Fernet(key)
        try:
            return fernet.decrypt(data)
        except InvalidToken as it:
            raise CryptError(f'Invalid token. Probably due to invalid password or key. '
                             f'Actual message: {it}')


