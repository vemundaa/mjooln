import uuid
import re


class IdentityError(Exception):

    def __init__(self, message):
        super().__init__(message)


class Identity(str):
    """UUID generator with convenience functions"""

    REGEX_STRING = r'[0-9A-F]{8}\_[0-9A-F]{4}\_[0-9A-F]{4}\_[0-9A-F]{4}' \
                   r'\_[0-9A-F]{12}'
    REGEX = re.compile(REGEX_STRING)

    @classmethod
    def isin(cls, text):
        if cls.REGEX.search(text):
            return True
        else:
            return False

    @classmethod
    def find_one(cls, text):
        res = cls.REGEX.search(text)
        if res:
            return cls(res.group())
        else:
            raise IdentityError(f'No identity found in this text: {text}. '
                                f'Consider using find_all, which will return '
                                f'empty list if no identities are found.')

    @classmethod
    def find_all(cls, text):
        ids = re.findall(cls.REGEX_STRING, text)
        return [cls(x) for x in ids]

    @classmethod
    def _verify_string(cls, identity_string):
        if cls.REGEX.match(identity_string) is None:
            raise IdentityError(f'String is not a valid identity: '
                                f'{identity_string}')

    def __new__(cls, identity=None):
        if not identity:
            identity = str(uuid.uuid4()).replace('-', '_').upper()
        elif isinstance(identity, Identity):
            # TODO: Decide on how to handle this...
            # identity = str(identity)
            # TODO: Make PythonicError? Or PythonicTrigger or similar
            # TODO: Make it possible to disable error, and handle it instead?
            raise IdentityError('It is not very pythonic to create an Identity from an Identity. '
                                'Use None or a valid string as input to this constructor, '
                                'or keep the object you already have.')
        else:
            cls._verify_string(identity)
        instance = super(Identity, cls).__new__(cls, identity)
        return instance

    @classmethod
    def elf(cls, identity):
        if isinstance(identity, Identity):
            return identity
        else:
            return cls(identity)


if __name__ == '__main__':
    id = Identity()
    print(id)
    id2 = Identity(str(id))
    print(id2)
