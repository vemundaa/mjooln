import logging
import string

logger = logging.getLogger(__name__)


class Key(str):
    """Defines key strings with limitations"""

    ALLOWED_CHARACTERS = string.ascii_lowercase + string.digits + '_'
    ALLOWED_STARTSWITH = string.ascii_lowercase
    MINIMUM_ALLOWED_LENGTH = 3
    RESERVED = '___'  # Used for separating key in segment
    SEPARATOR = '__'  # Separates groups in key

    def __new__(cls, key):
        if isinstance(key, Key):
            key = str(key)
        if not len(key) >= cls.MINIMUM_ALLOWED_LENGTH:
            raise KeyFormatError(f'Key too short. Key \'{key}\' has length {len(key)}, '
                                 f'while minimum length is {cls.MINIMUM_ALLOWED_LENGTH}')
        if not key[0] in cls.ALLOWED_STARTSWITH:
            raise KeyFormatError(f'Invalid startswith. '
                                 f'Key \'{key}\' cannot start with \'{key[0]}\'. '
                                 f'Allowed startswith characters are: {cls.ALLOWED_STARTSWITH}')
        invalid_characters = [x for x in key if x not in cls.ALLOWED_CHARACTERS]
        if len(invalid_characters) > 0:
            raise KeyFormatError(f'Invalid character(s). '
                                 f'Key \'{key}\' cannot contain any of {invalid_characters}. '
                                 f'Allowed characters are: {cls.ALLOWED_CHARACTERS}')
        if cls.RESERVED in key:
            raise KeyFormatError(f'Key contains reserved element. '
                                 f'Key \'{key}\' cannot contain \'{cls.RESERVED}\'')
        instance = super(Key, cls).__new__(cls, key)
        return instance

    def parts(self):
        return self.split(self.SEPARATOR)

    def with_separator(self, separator):
        return separator.join(self.parts())

    @classmethod
    def elf(cls, key):
        if isinstance(key, Key):
            return key
        else:
            return cls(key)


class PrivateKey(Key):

    ALLOWED_STARTSWITH = Key.ALLOWED_STARTSWITH + '_'


class KeyFormatError(Exception):
    pass
