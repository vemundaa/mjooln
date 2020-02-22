import logging

from mjooln import Zulu, Key, Identity

logger = logging.getLogger(__name__)


class Segment:

    SEPARATOR = '___'
    FORMAT = SEPARATOR.join(['{}', '{}', '{}'])

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
            if 'zulu' in kwargs:
                zulu = Zulu.elf(kwargs['zulu'])
            else:
                zulu = Zulu()
            if 'identity' in kwargs:
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
        return self.FORMAT.format(self.zulu, self.key, self.identity)

    # def dic(self):
    #     return {
    #         'key': self.key,
    #         'zulu': self.zulu,
    #         'identity': self.identity,
    #     }

    def parts(self):
        return str(self).split(self.SEPARATOR)

    def levels(self,
               key_levels=1,
               date_levels=1,
               time_levels=0):
        # TODO: Add negative input, to use as length of single key?
        if key_levels == 1:
            keys = [self.key]
        else:
            keys = self.key.parts()[:key_levels]

        zs = self.zulu.str
        if date_levels == 1:
            dates = [zs.date]
        else:
            dates = [zs.year, zs.month, zs.day][:date_levels]
        if time_levels == 1:
            times = [zs.time]
        else:
            times = [zs.hour, zs.minute, zs.second][:time_levels]

        return keys + dates + times


class SegmentError(Exception):
    pass


if __name__ == '__main__':
    zulu = Zulu()
    key = Key('t55t')
    ide = Identity()
    s = Segment(zulu, key, ide)
    print(s)

    ss = Segment('20191221T143324u113286Z___t55t___365E5E67_318A_497E_8FE6_7F1CC8974DFF')
    print(ss)

    s = Segment(key='test_it__again')
    print(s)
    print(s.branch(2,1,1))
