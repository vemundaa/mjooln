import logging
import datetime
import pytz
import dateutil
from dateutil.parser import parse as dateparser
import re

logger = logging.getLogger(__name__)


class ZuluStrings:

    def __init__(self, zulu):
        self.year = f'{zulu.year:04d}'
        self.month = f'{zulu.month:02d}'
        self.day = f'{zulu.day:02d}'
        self.hour = f'{zulu.hour:02d}'
        self.minute = f'{zulu.minute:02d}'
        self.second = f'{zulu.second:02d}'
        self.microsecond = f'{zulu.microsecond:06d}'
        self.date = self.year + self.month + self.day
        self.time = self.hour + self.minute + self.second


class Zulu(datetime.datetime):
    """Create timezone aware datetime objects in UTC

    file_stub creates a filename friendly format
    using format string: %Y%m%dT%H%M%Su%fZ
    from_file_stub finds and reads this date format from a string
    """

    FORMAT_STRING = '%Y%m%dT%H%M%Su%fZ'

    REGEX_STRING = r'\d{8}T\d{6}u\d{6}Z'
    REGEX = re.compile(REGEX_STRING)

    def __new__(cls, *args, **kwargs):
        if len(args) == 0:
            zulu = cls.utcnow().replace(tzinfo=pytz.UTC)
            zulu.str = ZuluStrings(zulu)
            return zulu
        if len(args) == 1:
            ts_utc = args[0]
            if isinstance(ts_utc, str):
                if len(ts_utc) == 23 and cls.REGEX.match(ts_utc):
                    return Zulu.parse(ts_utc, cls.FORMAT_STRING)
                else:
                    raise ZuluError(f'String is not Zulu-string. '
                                    f'Format should be: {Zulu()}')
            elif isinstance(ts_utc, float):
                zulu = cls.utcfromtimestamp(ts_utc). \
                    replace(tzinfo=pytz.UTC)
                zulu.str = ZuluStrings(zulu)
                return zulu
            elif isinstance(ts_utc, datetime.datetime):
                if not ts_utc.tzinfo == pytz.utc:
                    raise ZuluError('Cannot create Zulu from datetime if '
                                    'datetime object is not UTC')
                return Zulu(ts_utc.timestamp())
            elif isinstance(ts_utc, Zulu):
                raise ZuluError('Cannot create Zulu from Zulu')

        if len(args) < 8:
            # From date
            args = list(args)
            args += (8-len(args))*[0]
            args = tuple(args)

        if args[-1] not in [None, 0, pytz.utc]:
            raise ZuluError(f'Zulu can only be UTC. '
                            f'Invalid timezone: {args[-1]}')

        args = list(args)
        args[-1] = pytz.utc
        args = tuple(args)
        zulu = super(Zulu, cls).__new__(cls, *args, **kwargs)
        zulu.str = ZuluStrings(zulu)

        return zulu

    def __str__(self):
        return self.strftime(self.FORMAT_STRING)

    @classmethod
    def elf(cls, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0:
            maybe_zulu = args[0]
            if isinstance(maybe_zulu, Zulu):
                return maybe_zulu
            else:
                return cls(maybe_zulu)
        else:
            return cls(*args, **kwargs)

    @classmethod
    def string_elf(cls, maybe_zulu_string):
        try:
            ts = Zulu.from_iso_string(maybe_zulu_string)
            if Zulu.to_iso_string(ts) == maybe_zulu_string:
                return ts
        except ValueError:
            pass
        try:
            ts = Zulu(maybe_zulu_string)
            if str(ts) == maybe_zulu_string:
                return ts
        except ZuluError:
            pass
        return maybe_zulu_string

    @classmethod
    def from_unaware(cls, datetime_unaware):
        timestamp = datetime_unaware.\
                         replace(tzinfo=pytz.utc)
        return cls(timestamp)

    @classmethod
    def from_unaware_local(cls, datetime_local_unaware):
        datetime_local = datetime_local_unaware.\
                         replace(tzinfo=dateutil.tz.tzlocal())
        timestamp = datetime_local.astimezone(pytz.utc)
        return cls(timestamp)

    @classmethod
    def range(cls, start=None, n=10, delta=datetime.timedelta(hours=1)):
        if not start:
            start = cls()
        return [cls(start + x * delta) for x in range(n)]

    @classmethod
    def from_iso_string(cls, timestamp_string_iso):
        # TODO: Improve a bit
        timestamp = dateparser(timestamp_string_iso)
        if str(timestamp.tzinfo) == 'tzutc()':
            timestamp = timestamp.astimezone(pytz.utc)
        return Zulu(timestamp)

    def to_iso_string(self):
        return self.isoformat()

    @classmethod
    def parse(cls, string, pattern, is_local=False):
        ts = datetime.datetime.strptime(string, pattern)
        if is_local:
            return cls.from_unaware_local(ts)
        else:
            return cls(ts.replace(tzinfo=pytz.utc))

    def format(self, pattern):
        return self.strftime(pattern)


class ZuluError(Exception):
    pass


