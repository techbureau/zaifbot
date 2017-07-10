from abc import ABCMeta, abstractclassmethod


def Period(label_or_sec):
    for cls in _TradePeriod.__subclasses__():
        if isinstance(label_or_sec, str):
            if cls.is_my_label(label_or_sec):
                return cls(label_or_sec)
            continue

        if isinstance(label_or_sec, int):
            if cls.is_my_sec(label_or_sec):
                return cls(label_or_sec)
            continue
        raise ValueError


class _TradePeriod(metaclass=ABCMeta):
    _UTC_JP_DIFF = None

    def __init__(self, a):
        self._label = self.get_label()
        self._sec = self.get_sec()

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

    @abstractclassmethod
    def get_label(self):
        raise NotImplementedError

    @abstractclassmethod
    def get_sec(self):
        raise NotImplementedError

    @abstractclassmethod
    def is_my_label(self):
        raise NotImplementedError

    @abstractclassmethod
    def is_my_sec(self):
        raise NotImplementedError

    def truncate_sec(self, sec):
        if self.get_sec() > Period('1h').get_sec():
            return sec - ((sec + self._UTC_JP_DIFF) % self.get_sec())
        else:
            return sec - (sec % self.get_sec())

    def calc_count(self, start_sec, end_sec):
        round_end_sec = self.truncate_sec(end_sec)
        round_start_sec = self.truncate_sec(start_sec)
        count = int((round_end_sec - round_start_sec) / self.get_sec())
        return count

    def calc_start(self, count, end_sec):
        round_end_sec = self.truncate_sec(end_sec)
        start_sec = round_end_sec - self.get_sec() * count
        return start_sec


class _OneDay(_TradePeriod):
    def get_label(self):
        return '1d'

    def get_sec(self):
        return 86400

    @staticmethod
    def is_my_label(label):
        return label == '1d'

    @staticmethod
    def is_my_sec(sec):
        print(sec)
        return sec == 86400


class _TwelveHour(_TradePeriod):
    def get_label(self):
        return '12h'

    def get_sec(self):
        return 43200

    @staticmethod
    def is_my_label(label):
        return label == '12h'

    @staticmethod
    def is_my_sec(sec):
        return sec == 43200


class _EightHour(_TradePeriod):
    def get_label(self):
        return '8h'

    def get_sec(self):
        return 28800

    @staticmethod
    def is_my_label(label):
        return label == '8h'

    @staticmethod
    def is_my_sec(sec):
        return sec == 28800


class _FourHour(_TradePeriod):
    def get_label(self):
        return '4h'

    def get_sec(self):
        return 14400

    @staticmethod
    def is_my_label(label):
        return label == '4h'

    @staticmethod
    def is_my_sec(sec):
        return sec == 14400


class _OneHour(_TradePeriod):
    def get_label(self):
        return '1h'

    def get_sec(self):
        return 3600

    @staticmethod
    def is_my_label(label):
        return label == '1h'

    @staticmethod
    def is_my_sec(sec):
        return sec == 3600


class _ThirtyMinutes(_TradePeriod):
    def get_label(self):
        return '30m'

    def get_sec(self):
        return 1800

    @staticmethod
    def is_my_label(label):
        return label == '30m'

    @staticmethod
    def is_my_sec(sec):
        return sec == 1800


class _FifteenMinutes(_TradePeriod):
    def get_label(self):
        return '15m'

    def get_sec(self):
        return 900

    @staticmethod
    def is_my_label(label):
        return label == '15m'

    @staticmethod
    def is_my_sec(sec):
        return sec == 900


class _FiveMinutes(_TradePeriod):
    def get_label(self):
        return '5m'

    def get_sec(self):
        return 300

    @staticmethod
    def is_my_label(label):
        return label == '5m'

    @staticmethod
    def is_my_sec(sec):

        return sec == 300


class _OneMinute(_TradePeriod):
    def get_label(self):
        return '1m'

    def get_sec(self):
        return 60

    @staticmethod
    def is_my_label(label):
        return label == '1m'

    @staticmethod
    def is_my_sec(sec):
        return sec == 60
