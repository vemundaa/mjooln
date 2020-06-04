import logging
import datetime
import pytz
import dateutil
from dateutil.parser import parse as dateparser
import re

logger = logging.getLogger(__name__)


# TODO: Same date in all examples
# TODO: Move examples to separate documentation page?
class ZuluStrings:
    """Initializes convenience strings, and is instantiated with each Zulu
    object and stored in Zulu.str. Meant as the string version of the
    standard datetime.datetime integer values.

    Examples::

        z = Zulu('20200522T190137u055918Z')
        z.year
            2020
        z.str.year
            '2020'
        z.month
            5
        z.str.month
            '05'
        z.day
            22
        z.str.day
            '22'
        z.date()
            datetime.date(2020, 5, 22)
        z.str.date
            '20200522'
        z.time()
            datetime.time(19, 1, 37, 55918)
        z.str.time
            '190137'
        z.str.microsecond
            '055918'

        isinstance(z.str, ZuluStrings)
            True

    """
    def __init__(self, zulu):

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
    """Timezone aware datetime objects in UTC

    From constructor::

        Zulu() or Zulu.now()
            Zulu(2020, 5, 21, 20, 5, 31, 930343, tzinfo=<UTC>)

        Zulu(2020, 5, 12)
            Zulu(2020, 5, 12, 0, 0, tzinfo=<UTC>)

        Zulu(2020, 5, 21, 20, 5, 31)
            Zulu(2020, 5, 21, 20, 5, 31, tzinfo=<UTC>)

        Zulu('20200521T202041u590718Z')
            Zulu(2020, 5, 21, 20, 20, 41, 590718, tzinfo=<UTC>)

    Zulu String is on the format ``<date>T<time>u<microseconds>Z``, and is
    \'designed\'
    to be file name and double click friendly, as well as easily recognizable
    within some string when using regular expressions.
    Printing a Zulu object will result in this string, and the constructor
    can also be instantiated with it::

        z = Zulu(2020, 5, 12)
        print(z)
            20200512T000000u000000Z

        Zulu('20200521T202041u590718Z')
            Zulu(2020, 5, 21, 20, 20, 41, 590718, tzinfo=<UTC>)

    For an ISO 8601 formatted string, use custom function::

        z = Zulu('20200521T202041u590718Z')
        z.iso()
            '2020-05-21T20:20:41.590718+00:00'

    ISO strings can be parsed with a dedicated function, or with constructor::

        z = Zulu.parse_iso('2020-05-21T20:20:41.590718+00:00')
        print(z)
            20200521T202041u590718Z

        z = Zulu('2020-05-21T20:20:41.590718+00:00')
        print(z)
            20200521T202041u590718Z


    Inputs or constructors may vary, but Zulu objects are always UTC. Hence
    the name Zulu.

    Constructor also takes regular datetime objects, provided they have
    timezone info::

        dt = datetime.datetime(2020, 5, 23, tzinfo=pytz.utc)
        Zulu(dt)
            Zulu(2020, 5, 23, 0, 0, tzinfo=<UTC>)

        dt = datetime.datetime(2020, 5, 23, tzinfo=dateutil.tz.tzlocal())
        Zulu(dt)
            Zulu(2020, 5, 22, 22, 0, tzinfo=<UTC>)

    Examples::

        z = Zulu()
        print(z)
            20200522T190137u055918Z
        z.month
            5
        z.str.month
            '05'
        z.str.date
            '20200522'
        z.add(hours=2)
            Zulu(2020, 5, 22, 21, 1, 37, 55918, tzinfo=<UTC>)

    ``Zulu.elf()`` takes the same inputs as constructor, but also allowes
    Zulu objects to pass through. If timezone is missing, it will assume
    local. It can also be told to assume a specific timezone.

    """

    _FORMAT_STRING = '%Y%m%dT%H%M%Su%fZ'

    _REGEX_STRING = r'\d{8}T\d{6}u\d{6}Z'
    _REGEX = re.compile(_REGEX_STRING)

    # TODO: Expand testing

    @classmethod
    def now(cls, tz=None):
        """Overrides datetime.datetime.now(). Equivalent to Zulu()

        :param tz: Do not use. Zulu is always UTC
        :return: Zulu
        """
        if tz:
            raise ZuluError(f'Zulu.now() does not allow input time zone info. '
                            f'Zulu is always UTC. Hence the name')
        return cls()

    @classmethod
    def is_zulu(cls, ts_str):
        """ Checks if string is Zulu string

        .. note::  The function looks for Zulu String, not ISO 8601

        :param ts_str:
        :return:
        """
        return len(ts_str) == 23 and cls._REGEX.match(ts_str) is not None

    @classmethod
    def is_in(cls, text):
        """ Check if input text contains a zulu string

        .. note::  The function looks for Zulu String, not ISO 8601

        :type text: str
        :return: bool
        """
        if cls._REGEX.search(text):
            return True
        else:
            return False

    @classmethod
    def find_one(cls, text):
        """ Looks for and returns exactly one Zulu from text

        Will fail if there are none or multiple zulu\'s.
        Use find_all() to return a list of zulu\'s in text, including
        an empty list if there are none.

        .. note::  The function looks for Zulu String, not ISO 8601

        :type text: str
        :return: Zulu
        """
        res = cls._REGEX.search(text)
        if res:
            return cls(res.group())
        else:
            raise ZuluError(f'No zulu found in this text: {text}. '
                            f'Consider using find_all, which will return '
                            f'empty list if no zulu\'s are found.')

    @classmethod
    def find_all(cls, text):
        """ Finds and returns all zulu\'s in text

        Returns empty list if none are found.

        .. note::  The function looks for Zulu String, not ISO 8601

        :type text: str
        :return: [Zulu]
        """
        ids = re.findall(cls._REGEX_STRING, text)
        return [cls(x) for x in ids]

    @classmethod
    def _to_utc(cls, ts):
        return ts.astimezone(pytz.utc)

    @classmethod
    def _tz_from_name(cls, tz='utc'):
        if tz == 'local':
            tz = dateutil.tz.tzlocal()
        else:
            try:
                tz = pytz.timezone(tz)
            except pytz.exceptions.UnknownTimeZoneError as ue:
                raise ZuluError(f'Unknown timezone: \'{tz}\'. '
                                f'Use Zulu.all_timezones() for a list '
                                f'of actual timezones')
        return tz

    @classmethod
    def all_timezones(cls):
        """ Returns a list of all allowed timezone names, except \'local\',
        which will return a datetime object with local timezone

        Wrapper for pytz.all_timezones

        :return: list
        """
        return pytz.all_timezones

    @classmethod
    def _from_unaware(cls, ts, tz=None):
        if not tz:
            raise ZuluError('No timezone info. Set timezone to use '
                            'with \'tz=<timezone string>\'. \'local\' will '
                            'use local timezone info. Use '
                            'Zulu.all_timezones() for a list of actual '
                            'timezones')
        return ts.replace(tzinfo=cls._tz_from_name(tz))

    @classmethod
    def _elf(cls, ts, tz=None):
        if not ts.tzinfo:
            ts = cls._from_unaware(ts, tz=tz)
        return ts

    @classmethod
    def from_unaware(cls, ts, tz='utc'):
        """ Create Zulu from timezone unaware datetime

        :param ts: Unaware time stamp
        :type ts: datetime.datetime
        :param tz: Time zone, with 'utc' as default.
            'local' will use local time zone
        :return: Zulu
        """
        if ts.tzinfo:
            raise ZuluError(f'Input datetime already has '
                            f'time zone info: {ts}. '
                            f'Use constructor or Zulu.elf()')
        else:
            ts = cls._from_unaware(ts, tz=tz)
        return cls(ts)

    @classmethod
    def from_unaware_local(cls, ts):
        """ Create Zulu from timezone unaware local timestamp

        :param ts: Timezone unaware datetime
        :type ts: datetime.datetime
        :return: Zulu
        """
        return cls.from_unaware(ts, tz='local')

    @classmethod
    def from_unaware_utc(cls, ts):
        """ Create Zulu from timezone unaware UTC timestamp

        :param ts: Timezone unaware datetime
        :type ts: datetime.datetime
        :return: Zulu
        """
        return cls.from_unaware(ts, tz='utc')

    @classmethod
    def _parse_iso(cls, ts_str):
        ts = dateparser(ts_str)
        if ts.tzinfo:
            if str(ts.tzinfo) == 'tzutc()':
                ts = ts.astimezone(pytz.utc)
        return ts

    @classmethod
    def parse_iso(cls, ts_str, tz=None):
        """

        :param ts_str: ISO 8601 string
        :param tz: Timezone string to use if missing in ts_str
        :return:
        """
        ts = cls._parse_iso(ts_str)
        ts = cls._elf(ts, tz=tz)
        return cls(ts)

    @classmethod
    def _parse(cls, ts_str, pattern):
        return datetime.datetime.strptime(ts_str, pattern)

    @classmethod
    def _parse_zulu(cls, zulu_str):
        ts = cls._parse(zulu_str, cls._FORMAT_STRING)
        return cls._from_unaware(ts, tz='utc')

    @classmethod
    def parse(cls, ts_str, pattern, tz=None):
        """Parse time stamp string with the given pattern

        :param ts_str: Timestamp string
        :type ts_str: str
        :param pattern: Follows standard
            `python strftime reference <https://strftime.org/>`_
        :param tz: Timezone to use if timestamp does not have timezone info
        :return: Zulu
        """
        ts = cls._parse(ts_str, pattern)
        ts = cls._elf(ts, tz=tz)
        return cls(ts)

    @classmethod
    def is_iso(cls, ts_str):
        """Tests if the input string is in fact an
        `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ string

        .. note:: The test is made by converting the string to datetime
            and back again, making sure they are equal

        :param ts_str: Maybe an ISO formatted string
        :return: bool
        """
        try:
            ts = Zulu._parse_iso(ts_str)
            return ts.isoformat() == ts_str
        except ValueError:
            return False

    @classmethod
    def elf(cls, ts, tz='local'):
        """General input Zulu constructor

        Handles datetime.datetime, Zulu String, ISO 8601 string and epoch the
        same way as constructor. However, elf will assume local timezone if
        the input has no timezone info.

        .. warning:: Elves are fickle

        :param ts: Input time stamp
        :param tz: Time zone to assume if missing. 'local' will use local
            time zone. Use Zulu.all_timezones() for a list of actual
            timezones
        :return: Zulu
        """
        if isinstance(ts, Zulu):
            return ts
        elif isinstance(ts, datetime.datetime):
            ts = cls._elf(ts, tz=tz)
            return cls(ts)
        elif isinstance(ts, float):
            return cls(ts)
        elif isinstance(ts, str):
            if cls.is_zulu(ts):
                return cls(ts)
            elif cls.is_iso(ts):
                ts = cls._parse_iso(ts)
                ts = cls._elf(ts, tz=tz)
                return cls(ts)
            else:
                raise ZuluError(f'String is neither zulu, nor ISO: {ts}. '
                                f'Use Zulu.parse(). Or a different string')
        else:
            raise ZuluError(f'Found no way to interpret input '
                            f'as zulu: {ts}')

    @classmethod
    def range(cls,
              start=None,
              n=10,
              delta=datetime.timedelta(hours=1)):
        """Generate a list of Zulu of fixed intervals

        :param start: Start time Zulu, default is *now*
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
        # TODO: Cleanup instantiation (ZuluString is used three times)
        if len(args) == 0:
            zulu = cls.utcnow().replace(tzinfo=pytz.UTC)
            zulu.str = ZuluStrings(zulu)
            return zulu
        if len(args) == 1:
            ts_utc = args[0]
            if isinstance(ts_utc, str):
                if cls.is_zulu(ts_utc):
                    ts = cls._parse_zulu(ts_utc)
                    return Zulu(ts)
                elif cls.is_iso(ts_utc):
                    ts = cls._parse_iso(ts_utc)
                    if not ts.tzinfo:
                        raise ZuluError('Input string is iso, but does not '
                                        'have timezone info. Use Zulu.elf() '
                                        'with \'tz\'')
                    return Zulu(ts)
                else:
                    raise ZuluError(f'String is neither a valid ISO String, '
                                    f'nor Zulu String: {ts_utc}. '
                                    f'Use Zulu.parse()')
            elif isinstance(ts_utc, float):
                ts_utc = cls.utcfromtimestamp(ts_utc)
                ts_utc = ts_utc.replace(tzinfo=pytz.UTC)
                ts_utc.str = ZuluStrings(ts_utc)
                return ts_utc
            elif isinstance(ts_utc, Zulu):
                raise ZuluError('Cannot create Zulu object from Zulu object. '
                                'Use Zulu.elf() to allow this.')
            elif isinstance(ts_utc, datetime.datetime):
                if not ts_utc.tzinfo:
                    raise ZuluError('Cannot create Zulu from datetime if '
                                    'datetime object does not have timezone '
                                    'info. Use Zulu.from_unaware() or '
                                    'Zulu.elf() '
                                    'with \'tz\'')
                return Zulu(ts_utc.timestamp())

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

    def to_local(self):
        """ Create regular datetime with local timezone

        :return: datetime.datetime
        """
        return self.to_tz(tz='local')

    def to_tz(self, tz='local'):
        """ Create regular datetime with input timezone

        For a list of timezones::

            Zulu.dev_list_timezones()

        :param tz: Time zone to use. 'local' will return the local time zone
        :return: datetime.datetime
        """
        return self.astimezone(self._tz_from_name(tz))

    def format(self, pattern):
        """Format Zulu to string with the given pattern

        :param pattern: Follows standard
            `Python strftime reference <https://strftime.org/>`_
        :return: str
        """
        return self.strftime(pattern)

    @classmethod
    def delta(cls,
              days=0,
              hours=0,
              minutes=0,
              seconds=0,
              microseconds=0,
              weeks=0):
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
            days=0,
            hours=0,
            minutes=0,
            seconds=0,
            microseconds=0,
            weeks=0):
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
        return Zulu(self + delta)


class ZuluError(Exception):
    pass


