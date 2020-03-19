import os
import base64

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Crypt:
    """ Wrapper for best practice key generation and AES 128 encryption

    From Fernet doc:
    HMAC using SHA256 for authentication, and PKCS7 padding.
    Uses AES in CBC mode with a 128-bit key for encryption, and PKCS7 padding.
    """

    @classmethod
    def generate_key(cls):
        """ Returns URL-safe base64-encoded random key with length 44 """
        return Fernet.generate_key()

    @classmethod
    def salt(cls):
        """ Returns URL-safe base64-encoded random string with length 24 """

        # Used 18 instead of standard 16 since encode otherwise leaves
        # two trailing equal signs (==)
        return base64.urlsafe_b64encode(os.urandom(18))

    @classmethod
    def key_from_password(cls, salt, password):
        """ Returns URL-safe base64-encoded random string with length 44 """

        password = password.encode()  # Convert to type bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

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
        if not type(data) == bytes:
            raise CryptError('Cannot decrypt data. Data is not bytes')
        if not type(key) == bytes:
            raise CryptError('Cannot decrypt data. Key is not bytes')
        fernet = Fernet(key)
        try:
            return fernet.decrypt(data)
        except InvalidToken as it:
            raise CryptError(f'Invalid token. Probably due to invalid password/key. '
                             f'Actual message: {it}')


class CryptError(Exception):
    pass

