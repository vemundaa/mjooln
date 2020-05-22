import uuid
import re


class IdentityError(Exception):
    pass


class Identity(str):
    """ UUID string generator with convenience functions

    Inherits str, and is therefore an immutable string, with a fixed format
    as illustrated below.

    Examples::

        Identity()
            'BD8E446D_3EB9_4396_8173_FA1CF146203C'

        Identity.is_in('Has BD8E446D_3EB9_4396_8173_FA1CF146203C within')
            True

        Identity.find_one('Has BD8E446D_3EB9_4396_8173_FA1CF146203C within')
            'BD8E446D_3EB9_4396_8173_FA1CF146203C'

    """

    _REGEX_STRING = r'[0-9A-F]{8}\_[0-9A-F]{4}\_[0-9A-F]{4}\_[0-9A-F]{4}' \
                   r'\_[0-9A-F]{12}'
    _REGEX = re.compile(_REGEX_STRING)

    @classmethod
    def is_in(cls, text):
        """ Check if input text contains an identity

        :type text: str
        :return: bool
        """
        if cls._REGEX.search(text):
            return True
        else:
            return False

    @classmethod
    def find_one(cls, text):
        """ Looks for and returns exactly one Identity from text

        Will fail if there are none or multiple identities.
        Use find_all() to return a list of identities in text, including
        an empty list if there are none.

        :type text: str
        :return: Identity
        """
        res = cls._REGEX.search(text)
        if res:
            return cls(res.group())
        else:
            raise IdentityError(f'No identity found in this text: {text}. '
                                f'Consider using find_all, which will return '
                                f'empty list if no identities are found.')

    @classmethod
    def find_all(cls, text):
        """ Finds and returns all identities in text

        :type text: str
        :return: [Identity]
        """
        ids = re.findall(cls._REGEX_STRING, text)
        return [cls(x) for x in ids]

    @classmethod
    def _verify_string(cls, identity_string):
        if cls._REGEX.match(identity_string) is None:
            raise IdentityError(f'String is not a valid identity: '
                                f'{identity_string}')

    def __new__(cls, identity=None):
        if not identity:
            identity = str(uuid.uuid4()).replace('-', '_').upper()
        elif isinstance(identity, Identity):
            raise IdentityError('It is not very pythonic to create an Identity '
                                'from an Identity. Use None or a valid string '
                                'as input to this constructor, or keep the '
                                'object you already have. Another alternative '
                                'is to use Identity.elf()')
        else:
            cls._verify_string(identity)
        instance = super(Identity, cls).__new__(cls, identity)
        return instance

    @classmethod
    def elf(cls, identity):
        """ Returns new or existing identity

        None will create a new Identity, a string will be parsed as Identity,
        and an existing Identity will be returned as itself.

        :type identity: None, str or Identity
        :return: Identity
        """
        if isinstance(identity, Identity):
            return identity
        else:
            return cls(identity)

