import os
import base64

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Crypt:
    """ Wrapper for best practice key generation and AES 128 encryption

    From `Fernet Docs <https://cryptography.io/en/latest/fernet/>`_:
    HMAC using SHA256 for authentication, and PKCS7 padding.
    Uses AES in CBC mode with a 128-bit key for encryption, and PKCS7 padding.
    """

    # TODO: Do QA on cryptographic strength

    @classmethod
    def generate_key(cls):
        """ Generates URL-safe base64-encoded random key with length 44 """
        return Fernet.generate_key()

    @classmethod
    def salt(cls):
        """ Generates URL-safe base64-encoded random string with length 24

        :return: bytes
        """

        # Used 18 instead of standard 16 since encode otherwise leaves
        # two trailing equal signs (==) in the resulting string
        return base64.urlsafe_b64encode(os.urandom(18))

    @classmethod
    def key_from_password(cls, salt, password):
        """ Generates URL-safe base64-encoded random string with length 44

        :type salt: bytes
        :type password: str
        :return: bytes
        """

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
        """ Encrypts input data with the given key

        :type data: bytes
        :type key: bytes
        :return: bytes
        """
        if not type(data) == bytes:
            raise CryptError('Cannot encrypt data. Data is not bytes')
        if not type(key) == bytes:
            raise CryptError('Cannot encrypt data. Key is not bytes')
        fernet = Fernet(key)
        return fernet.encrypt(data)

    @classmethod
    def decrypt(cls, data, key):
        """ Decrypts input data with the given key

        :type data: bytes
        :type key: bytes
        :return: bytes
        """
        if not type(data) == bytes:
            raise CryptError('Cannot decrypt data. Data is not bytes')
        if not type(key) == bytes:
            raise CryptError('Cannot decrypt data. Key is not bytes')
        fernet = Fernet(key)
        try:
            return fernet.decrypt(data)
        except InvalidToken as it:
            raise CryptError(f'Invalid token. Probably due to '
                             f'invalid password/key. Actual message: {it}')


class CryptError(Exception):
    pass

