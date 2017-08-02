from abc import ABCMeta, abstractclassmethod


def Period(period):
    for cls in _TradePeriod.__subclasses__():
        if isinstance(period, str):
            if cls.is_my_label(period):
                return cls(period)
            continue

        if isinstance(period, int):
            if cls.is_my_sec(period):
                return cls(period)
            continue

        if isinstance(period, _TradePeriod):
            return period

        raise ValueError('illegal argument received')


class _TradePeriod(metaclass=ABCMeta):
    _UTC_JP_DIFF = 32400

    def __init__(self, a):
        self._label = self.label
        self._sec = self.sec

    def __str__(self):
        return self._label

    def __int__(self):
        return self._sec

    def __eq__(self, other):
        if isinstance(other, _TradePeriod):
            return self._label == other._label
        if isinstance(other, str):
            return self._label == other
        if isinstance(other, int):
            return self._sec == other
        return False

    @property
    @abstractclassmethod
    def label(self):
        raise NotImplementedError

    @property
    @abstractclassmethod
    def sec(self):
        raise NotImplementedError

    @abstractclassmethod
    def is_my_label(self):
        raise NotImplementedError

    @abstractclassmethod
    def is_my_sec(self):
        raise NotImplementedError

    def truncate_sec(self, sec):
        if self.sec > Period('1h').sec:
            return sec - ((sec + self._UTC_JP_DIFF) % self.sec)
        else:
            return sec - (sec % self.sec)

    def calc_count(self, start_sec, end_sec):
        round_end_sec = self.truncate_sec(end_sec)
        round_start_sec = self.truncate_sec(start_sec)
        count = int((round_end_sec - round_start_sec) / self.sec)
        return count

    def calc_start(self, count, end_sec):
        round_end_sec = self.truncate_sec(end_sec)
        start_sec = round_end_sec - self.sec * (count -1)
        return start_sec


class _OneDay(_TradePeriod):
    @property
    def label(self):
        return '1d'

    @property
    def sec(self):
        return 86400

    @staticmethod
    def is_my_label(label):
        return label == '1d'

    @staticmethod
    def is_my_sec(sec):
        return sec == 86400


class _TwelveHour(_TradePeriod):
    @property
    def label(self):
        return '12h'

    @property
    def sec(self):
        return 43200

    @staticmethod
    def is_my_label(label):
        return label == '12h'

    @staticmethod
    def is_my_sec(sec):
        return sec == 43200


class _EightHour(_TradePeriod):
    @property
    def label(self):
        return '8h'

    @property
    def sec(self):
        return 28800

    @staticmethod
    def is_my_label(label):
        return label == '8h'

    @staticmethod
    def is_my_sec(sec):
        return sec == 28800


class _FourHour(_TradePeriod):
    @property
    def label(self):
        return '4h'

    @property
    def sec(self):
        return 14400

    @staticmethod
    def is_my_label(label):
        return label == '4h'

    @staticmethod
    def is_my_sec(sec):
        return sec == 14400


class _OneHour(_TradePeriod):
    @property
    def label(self):
        return '1h'

    @property
    def sec(self):
        return 3600

    @staticmethod
    def is_my_label(label):
        return label == '1h'

    @staticmethod
    def is_my_sec(sec):
        return sec == 3600


class _ThirtyMinutes(_TradePeriod):
    @property
    def label(self):
        return '30m'

    @property
    def sec(self):
        return 1800

    @staticmethod
    def is_my_label(label):
        return label == '30m'

    @staticmethod
    def is_my_sec(sec):
        return sec == 1800


class _FifteenMinutes(_TradePeriod):
    @property
    def label(self):
        return '15m'

    @property
    def sec(self):
        return 900

    @staticmethod
    def is_my_label(label):
        return label == '15m'

    @staticmethod
    def is_my_sec(sec):
        return sec == 900


class _FiveMinutes(_TradePeriod):
    @property
    def label(self):
        return '5m'

    @property
    def sec(self):
        return 300

    @staticmethod
    def is_my_label(label):
        return label == '5m'

    @staticmethod
    def is_my_sec(sec):

        return sec == 300


class _OneMinute(_TradePeriod):
    @property
    def label(self):
        return '1m'

    @property
    def sec(self):
        return 60

    @staticmethod
    def is_my_label(label):
        return label == '1m'

    @staticmethod
    def is_my_sec(sec):
        return sec == 60
