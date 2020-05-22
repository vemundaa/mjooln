import logging
import datetime
import pytz
import dateutil
from dateutil.parser import parse as dateparser
import re

logger = logging.getLogger(__name__)


class ZuluStrings:

    def __init__(self, zulu):
        """Initializes individual strings, and included in each Zulu object

        :param zulu: Input date
        """
        # Year
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
    """Time zone aware datetime objects in UTC

    From constructor::

        Zulu() or Zulu.now()
            Zulu(2020, 5, 21, 20, 5, 31, 930343, tzinfo=<UTC>)

        Zulu(2020, 5, 12)
            Zulu(2020, 5, 12, 0, 0, tzinfo=<UTC>)

        Zulu(2020, 5, 21, 20, 5, 31)
            Zulu(2020, 5, 21, 20, 5, 31, tzinfo=<UTC>)

        Zulu('20200521T202041u590718Z')
            Zulu(2020, 5, 21, 20, 20, 41, 590718, tzinfo=<UTC>)


    Inputs or constructors may vary, but any return will have time zone
    UTC. Hence the name Zulu.
    """

    _FORMAT_STRING = '%Y%m%dT%H%M%Su%fZ'

    _REGEX_STRING = r'\d{8}T\d{6}u\d{6}Z'
    _REGEX = re.compile(_REGEX_STRING)

    @classmethod
    def now(cls, tz=None):
        """Overrides datetime.datetime.now(). Equivalent to Zulu()

        :param tz: Do not use. Zulu is always UTC
        :return: Zulu
        """
        if tz:
            raise ZuluError(f'Zulu.now() does not allow input time zone info. '
                            f'Zulu is always UTC')
        return cls()

    @classmethod
    def _aware(cls, ts):
        return ts.astimezone(pytz.utc)

    @classmethod
    def aware(cls, ts):
        """Create Zulu from time zone aware datetime

        :param ts: Time zone aware datetime
        :type ts: datetime.datetime
        :return: Zulu
        """
        if not ts.tzinfo:
            raise ZuluError(f'Input is not time zone aware. '
                            f'Use Zulu.elf()')
        ts = cls._aware(ts)
        return cls(ts)

    @classmethod
    def _unaware(cls, ts, assume='utc'):
        if assume in ['utc', 'UTC']:
            ts = ts.replace(tzinfo=pytz.utc)
        elif assume == 'local':
            ts = ts.replace(tzinfo=dateutil.tz.tzlocal())
        else:
            ts = ts.replace(tzinfo=dateutil.tz.gettz(name=assume))
        return ts

    @classmethod
    def unaware(cls, ts, tz='utc'):
        """ Create Zulu from unaware datetime

        :param ts: Unaware time stamp
        :type ts: datetime.datetime
        :param tz: Time zone, with 'utc' as default.
            'local' will use local time zone
        :return: Zulu
        """
        if ts.tzinfo:
            raise ZuluError(f'Input datetime already has '
                            f'time zone info: {ts}. '
                            f'Use Zulu.elf()')
        else:
            ts = cls._unaware(ts, assume=tz)
        return cls.aware(ts)

    @classmethod
    def local(cls, ts):
        """ Create Zulu from local time zone unaware timestamp

        :param ts: Time zone unaware datetime
        :type ts: datetime.datetime
        :return: Zulu
        """
        return cls.unaware(ts, tz='local')

    @classmethod
    def _parse_iso(cls, ts_str):
        ts = dateparser(ts_str)
        if ts.tzinfo:
            if str(ts.tzinfo) == 'tzutc()':
                ts = ts.astimezone(pytz.utc)
        return ts

    @classmethod
    def parse_iso(cls, ts_str):
        """Create Zulu from ISO 8601 string

        :param ts_str: ISO 8601 string
        :type ts_str: str
        :return: Zulu
        """
        ts = cls._parse_iso(ts_str)
        if not ts.tzinfo:
            raise ZuluError(f'ISO string does not have time zone info. '
                            f'Use Zulu.parse_iso_elf()')
        return Zulu.aware(ts)

    @classmethod
    def parse_iso_elf(cls, ts_str, tz_assume='utc'):
        """Parse `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ string,
        and assume time zone if missing

        :param ts_str: ISO 8601 string
        :type ts_str: str
        :param tz_assume: Time zone to assume if missing.
            'local' assumes local time zone
        :type tz_assume: str
        :return: Zulu
        """
        ts = cls._parse_iso(ts_str)
        if not ts.tzinfo:
            return cls.unaware(ts, tz=tz_assume)
        else:
            return cls.aware(ts)

    @classmethod
    def _parse(cls, ts_str, pattern):
        return datetime.datetime.strptime(ts_str, pattern)

    @classmethod
    def parse(cls, ts_str, pattern):
        """Parse time stamp string with the given pattern

        :param ts_str: Time stamp string
        :type ts_str: str
        :param pattern: Follows standard
            `python strftime reference <https://strftime.org/>`_
        :return:
        """
        ts = cls._parse(ts_str, pattern)
        if not ts.tzinfo:
            raise ZuluError(f'String does not have time zone info: {ts_str}. '
                            f'Use Zulu.parse_elf()')
        else:
            return cls.aware(ts)

    @classmethod
    def parse_elf(cls, ts_str, pattern, tz_assume='utc'):
        """Parse time stamp string, and assume time zone if missing

        :param ts_str: Time stamp string
        :type ts_str: str
        :param pattern: Follows standard
            `python strftime reference <https://strftime.org/>`_
        :param tz_assume: Time zone to assume if missing.
            'local' assumes local time zone
        :type tz_assume: str
        :return: Zulu
        """
        ts = cls._parse(ts_str, pattern)
        if not ts.tzinfo:
            return cls.unaware(ts, tz=tz_assume)
        else:
            return cls.aware(ts)

    @classmethod
    def is_zulu_str(cls, ts_str):
        return len(ts_str) == 23 and cls._REGEX.match(ts_str)

    @classmethod
    def _parse_zulu(cls, zulu_str):
        return Zulu.parse_elf(zulu_str, cls._FORMAT_STRING)

    @classmethod
    def parse_zulu(cls, zulu_str):
        if cls.is_zulu_str(zulu_str):
            return cls._parse_zulu(zulu_str)
        else:
            raise ZuluError(f'String is not zulu format: {zulu_str}. '
                            f'Should be on format: {cls()}. '
                            f'Use Zulu.parse()')

    @classmethod
    def is_iso_str(cls, ts_str):
        """Tests if the input string is in fact an
        `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ string

        :param ts_str: Maybe an ISO formatted string
        :return: bool
        """
        try:
            ts = Zulu.parse_iso(ts_str)
            return Zulu.iso(ts) == ts_str
        except ValueError:
            return False

    @classmethod
    def elf(cls, ts, tz_assume='utc'):
        """General input Zulu constructor

        Handles datetime.datetime with or without time zone info, Zulu string,
        ISO 8601 string and epoch.

        :param ts: Input time stamp
        :param tz_assume: Time zone to assume if missing.
            'local' will use local time zone
        :return: Zulu
        """
        if isinstance(ts, Zulu):
            return ts
        elif isinstance(ts, datetime.datetime):
            if ts.tzinfo:
                return cls.aware(ts)
            else:
                return cls.unaware(ts, tz=tz_assume)
        elif isinstance(ts, float):
            return cls(ts)
        elif isinstance(ts, str):
            if cls.is_zulu_str(ts):
                return cls.parse_zulu(ts)
            elif cls.is_iso_str(ts):
                return cls.parse_iso_elf(ts, tz_assume=tz_assume)
            else:
                raise ZuluError(f'String is neither zulu, nor ISO: {ts}. '
                                f'Use Zulu.parse()')
        else:
            raise ZuluError(f'Found no way to interpret input '
                            f'as zulu: {ts}')

    @classmethod
    def range(cls,
              start=None,
              n=10,
              delta=datetime.timedelta(hours=1)):
        """Generate a list of Zulu of fixed intervals

        :param start: Start time Zulu, default is now
        :type start: Zulu
        :param n: Number of timestamps in range, with default 10
        :type n: int
        :param delta: Time delta between items, with default one hour
        :type delta: datetime.timedelta
        :return: [Zulu]
        """
        if not start:
            start = cls()
        return [cls(start + x * delta) for x in range(n)]

    def __new__(cls, *args, **kwargs):
        if len(args) == 0:
            zulu = cls.utcnow().replace(tzinfo=pytz.UTC)
            zulu.str = ZuluStrings(zulu)
            return zulu
        if len(args) == 1:
            ts_utc = args[0]
            if isinstance(ts_utc, str):
                if cls.is_zulu_str(ts_utc):
                    return cls.parse_zulu(ts_utc)
                else:
                    raise ZuluError(f'String is not zulu string: {ts_utc}. '
                                    f'Use Zulu.parse()')
            elif isinstance(ts_utc, float):
                ts_utc = cls.utcfromtimestamp(ts_utc)
                ts_utc = ts_utc.replace(tzinfo=pytz.UTC)
                ts_utc.str = ZuluStrings(ts_utc)
                return ts_utc
            elif isinstance(ts_utc, datetime.datetime):
                if not ts_utc.tzinfo == pytz.utc:
                    raise ZuluError('Cannot create Zulu from datetime if '
                                    'datetime object is not UTC. '
                                    'Use Zulu.elf() or Zulu.ts_elf()')
                return Zulu(ts_utc.timestamp())
            elif isinstance(ts_utc, Zulu):
                raise ZuluError('Cannot instantiate Zulu from Zulu. '
                                'Use Zulu.elf()')

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
        return self.strftime(self._FORMAT_STRING)

    def iso(self):
        """Create `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ string

        Example::

            z = Zulu(2020, 5, 21)
            z.iso()
                '2020-05-21T00:00:00+00:00'

        :return: str
        """
        return self.isoformat()

    def format(self, pattern):
        """Format Zulu to string with the given pattern

        :param pattern: Follows standard
            `python strftime reference <https://strftime.org/>`_
        :return: str
        """
        return self.strftime(pattern)

    def delta(self,
              days=None,
              hours=None,
              minutes=None,
              seconds=None,
              microseconds=None,
              weeks=None):
        """Wrapper for datetime.timedelta

        :param days: Number of days
        :param hours: Number of hours
        :param minutes: Number of minutes
        :param seconds: Number of seconds
        :param microseconds: Number of microseconds
        :param weeks: Number of weeks
        :return: datetime.timedelta
        """
        return datetime.timedelta(days=days,
                                  hours=hours,
                                  minutes=minutes,
                                  seconds=seconds,
                                  microseconds=microseconds,
                                  weeks=weeks)

    def add(self,
            days=None,
            hours=None,
            minutes=None,
            seconds=None,
            microseconds=None,
            weeks=None):
        """Adds the input to current Zulu object and returns a new one

        :param days: Number of days
        :param hours: Number of hours
        :param minutes: Number of minutes
        :param seconds: Number of seconds
        :param microseconds: Number of microseconds
        :param weeks: Number of weeks
        :return: Zulu
        """
        delta = self.delta(days=days,
                           hours=hours,
                           minutes=minutes,
                           seconds=seconds,
                           microseconds=microseconds,
                           weeks=weeks)
        return self + delta


class ZuluError(Exception):
    pass


