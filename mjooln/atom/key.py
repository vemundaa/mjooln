import logging
import string

logger = logging.getLogger(__name__)


class Key(str):
    """ Defines key strings with limitations

    - Minimum length is 3
    - Allowed characters are
        - Lower case ascii (a-z)
        - Digits (0-9)
        - Underscore (_)
        - Double underscore (__)
    - The double underscore act as separator for groups in the key
    - Triple underscore is reserved for separating keys from other strings,
        such as in class :class:`.Atom`

    Sample keys::

        '_some_private_key'
        'simple'
        'group_one__group_two__group_three'

    """

    _ALLOWED_CHARACTERS = string.ascii_lowercase + string.digits + '_'
    _ALLOWED_STARTSWITH = string.ascii_lowercase
    _MINIMUM_ALLOWED_LENGTH = 3
    _RESERVED = '___'  # Used for separating key in segment
    _SEPARATOR = '__'  # Separates groups in key

    def __new__(cls, key):
        if isinstance(key, Key):
            key = str(key)
        if not len(key) >= cls._MINIMUM_ALLOWED_LENGTH:
            raise KeyFormatError(f'Key too short. Key \'{key}\' has length '
                                 f'{len(key)}, while minimum length is '
                                 f'{cls._MINIMUM_ALLOWED_LENGTH}')
        if not key[0] in cls._ALLOWED_STARTSWITH:
            raise KeyFormatError(f'Invalid startswith. Key \'{key}\' cannot '
                                 f'start with \'{key[0]}\'. Allowed startswith '
                                 f'characters are: {cls._ALLOWED_STARTSWITH}')
        invalid_characters = [x for x in key if x not in
                              cls._ALLOWED_CHARACTERS]
        if len(invalid_characters) > 0:
            raise KeyFormatError(f'Invalid character(s). Key \'{key}\' cannot '
                                 f'contain any of {invalid_characters}. '
                                 f'Allowed characters are: '
                                 f'{cls._ALLOWED_CHARACTERS}')
        if cls._RESERVED in key:
            raise KeyFormatError(f'Key contains reserved element. '
                                 f'Key \'{key}\' cannot contain '
                                 f'\'{cls._RESERVED}\'')
        instance = super(Key, cls).__new__(cls, key)
        return instance

    def parts(self):
        """ Returns key parts as defined by separator (double underscore)

        Example::

            key = Key('some_key__with_two__three_parts')
            key.parts()
                ['some_key', 'with_two', 'three_parts']

        :returns: [str]
        """
        return self.split(self._SEPARATOR)

    def with_separator(self, separator):
        """ Replace separator

        Example::

            key = Key('some__key_that_could_be__path')
            key.with_separator('/')
                'some/key_that_could_be/path'

        :param separator: Separator of choice
        :type separator: str
        :return: str
        """
        return separator.join(self.parts())

    @classmethod
    def elf(cls, key):
        """ Allows key class to pass through instead of throwing exception

        :type key: str or Key
        :return: Key
        """
        if isinstance(key, Key):
            return key
        else:
            return cls(key)


class KeyFormatError(Exception):
    pass
