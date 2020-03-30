import logging

from mjooln.core.zulu import Zulu
from mjooln.core.key import Key
from mjooln.core.identity import Identity

logger = logging.getLogger(__name__)


class Segment:

    SEPARATOR = '___'
    LEVEL_FULL = 100
    LEVEL_NONE = 0

    @classmethod
    def check(cls, dic):
        keys = dic.keys()
        if len(keys) == 3:
            if 'key' in keys and 'zulu' in keys and 'identity' in keys:
                return True
        return False

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            z, k, i = args[0].split(self.SEPARATOR)
            zulu = Zulu.elf(z)
            key = Key.elf(k)
            identity = Identity.elf(i)
        elif len(args) == 3:
            zulu, key, identity = args
            if not isinstance(zulu, Zulu):
                raise SegmentError(f'\'{zulu}\' is not Zulu object')
            if not isinstance(key, Key):
                raise SegmentError(f'\'{key}\' is not Key object')
            if not isinstance(identity, Identity):
                raise SegmentError(f'\'{identity}\' is not Identity Object')
        elif len(kwargs) >= 1 and 'key' in kwargs:
            key = Key.elf(kwargs['key'])
            if 'zulu' in kwargs and kwargs['zulu']:
                zulu = Zulu.elf(kwargs['zulu'])
            else:
                zulu = Zulu()
            if 'identity' in kwargs and kwargs['identity']:
                identity = Identity.elf(kwargs['identity'])
            else:
                identity = Identity()
        else:
            raise SegmentError(f'Invalid arguments: {args}'
                               f'And/or invalid keyword arguments: {kwargs}')

        self.zulu = zulu
        self.key = key
        self.identity = identity

    def __str__(self):
        return self.SEPARATOR.join([str(self.zulu), self.key, self.identity])

    def dic(self):
        return vars(self)

    def custom_separator(self, separator):
        return separator.join(str(self).split(self.SEPARATOR))

    def levels(self,
               key_level=LEVEL_FULL,
               date_level=LEVEL_FULL,
               time_level=0):
        # TODO: Refactor to find a way to have a second version of 0. Or int with direction?
        if key_level == self.LEVEL_FULL:
            keys = [self.key]
        else:
            keys = self.key.parts()[:abs(key_level)]
        if key_level < 0:
            keys = [''.join(keys)]

        zs = self.zulu.str
        if date_level == self.LEVEL_FULL:
            dates = [zs.date]
        else:
            dates = [zs.year, zs.month, zs.day][:abs(date_level)]
        if date_level < 0:
            dates = [''.join(dates)]

        if time_level == self.LEVEL_FULL:
            times = [zs.time]
        else:
            times = [zs.hour, zs.minute, zs.second][:abs(time_level)]
        if time_level < 0:
            times = [''.join(times)]

        return keys + dates + times


class SegmentError(Exception):
    pass

#
# if __name__ == '__main__':
#     zulu = Zulu()
#     key = Key('t55t')
#     ide = Identity()
#     s = Segment(zulu, key, ide)
#     print(s)
#
#     ss = Segment('20191221T143324u113286Z___t55t___365E5E67_318A_497E_8FE6_7F1CC8974DFF')
#     print(ss)
#
#     s = Segment(key='test_it__again')
#     print(s)
#     print(s.branch(2,1,1))
