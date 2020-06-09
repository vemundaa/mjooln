import logging

from mjooln.atom.zulu import Zulu
from mjooln.atom.key import Key
from mjooln.atom.identity import Identity

logger = logging.getLogger(__name__)


class AtomError(Exception):
    pass


class Atom:
    """ Unique identifier intended for objects and data sets alike

    The timestamp (zulu) defines start time (t0) of data set, or the time of
    creation. Key defines the grouping, while identity is a unique UUID

    Format: ``<zulu>___<key>___<identity>``

    :class:`.Zulu` represents t0 or creation time

    :class:`.Key` defines grouping of the contents

    :class:`.Identity` is a unique identifier for the contents

    Constructor initializes a valid atom, and will throw an exception
    if a valid atom cannot be created based on input parameters.

    The constructor must as minimum have ``key`` as input::

        a = Atom(key='some_key')
        a.key
            'some_key'
        a.zulu
            Zulu(2020, 5, 22, 13, 13, 18, 179169, tzinfo=<UTC>)
        a.identity
            '060AFBD5_D865_4974_8E37_FDD5C55E7CD8'
        str(a)
            '20200522T131318u179169Z___some_key___060AFBD5_D865_4974_8E37_FDD5C55E7CD8'

    """

    #: Separates elements in atom string
    SEPARATOR = Key.OUTER_SEPARATOR


    @classmethod
    def check(cls, dic):
        """ Check if the input dictionary represents a valid atom

        :param dic: Input dictionary
        :type dic: dict
        :return: bool
        """
        keys = dic.keys()
        if len(keys) == 3:
            if 'key' in keys and 'zulu' in keys and 'identity' in keys:
                return True
        return False

    @classmethod
    def elf(cls, *args, **kwargs):
        if len(args) == 1 and kwargs is None and isinstance(args[0], Atom):
            return args[0]
        else:
            return cls(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        """ Initializes a valid atom

        :param args: One argument is treated as a atom string and parsed.
        Three arguments is treated as (zulu, key, identity), in that order.
        :param kwargs: key, zulu, identity. key is required, while zulu and
        identity are created if not supplied.
        """
        if len(args) == 1:
            try:
                z, k, i = args[0].split(self.SEPARATOR)
            except ValueError as ve:
                raise AtomError(f'Invalid input: {args[0]}')
            zulu = Zulu.elf(z)
            key = Key.elf(k)
            identity = Identity.elf(i)
        elif len(args) == 3:
            zulu, key, identity = args
            if not isinstance(zulu, Zulu):
                raise AtomError(f'\'{zulu}\' is not Zulu object')
            if not isinstance(key, Key):
                raise AtomError(f'\'{key}\' is not Key object')
            if not isinstance(identity, Identity):
                raise AtomError(f'\'{identity}\' is not Identity Object')
        elif len(kwargs) >= 1 and 'key' in kwargs:
            key = Key.elf(kwargs['key'])
            if 'zulu' in kwargs:
                zulu = Zulu.elf(kwargs['zulu'])
            else:
                zulu = Zulu()
            if 'identity' in kwargs:
                identity = Identity.elf(kwargs['identity'])
            else:
                identity = Identity()
        else:
            raise AtomError(f'Invalid arguments: {args}'
                            f'And/or invalid keyword arguments: {kwargs}')

        self.zulu = zulu
        self.key = key
        self.identity = identity

    def __str__(self):
        return self.SEPARATOR.join([str(self.zulu), self.key, self.identity])

    def custom_separator(self, separator):
        """ Atom string with custom separator

        :param separator: Custom separator
        :return: str
        """
        return separator.join(str(self).split(self.SEPARATOR))

    def levels(self,
               key_level=None,
               date_level=None,
               time_level=0):
        """ Create list of levels representing the Atom

        Intended usage is for creating folder paths for atom files

        **None**: Full value

        **0**: No value

        **Negative**: Number of elements as string

        **Positive**: Number of elements as list

        Example::

            a = Atom(key='this__is__a_key')
            str(a)
                '20200522T181551u626184Z___this__is__a_key___F45A9C74_DC5D_48A6_9468_FC7E343EC554'
            a.levels()
                ['this__is__a_key', '20200522']
            a.levels(None, None, None)
                ['this__is__a_key', '20200522', '181551']
            a.levels(0, 0, 0)
                []
            a.levels(3, 2, 1)
                ['this', 'is', 'a_key', '2020', '05', '18']
            a.levels(-3, -2, -1)
                ['this__is__a_key', '202005', '18']

        :param key_level: Key levels
        :param date_level: Date levels
        :param time_level: Time levels
        :return: list
        """

        def make(parts, level, sep=''):
            if level == 0:
                return []
            elif level > 0:
                return parts[:level]
            else:
                return [sep.join(parts[:-level])]

        if key_level is None:
            keys = [self.key]
        else:
            keys = make(self.key.parts(), key_level, sep='__')

        zs = self.zulu.str
        if date_level is None:
            dates = [zs.date]
        else:
            dates = make([zs.year, zs.month, zs.day], date_level)
        if time_level is None:
            times = [zs.time]
        else:
            times = make([zs.hour, zs.minute, zs.second], time_level)

        return keys + dates + times
