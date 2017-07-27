import unittest
from zaifbot.exchange import Period


class TestPeriod(unittest.TestCase):
    one_day = Period('1d')
    labels = [
        '1d',
        '12h',
        '8h',
        '4h',
        '1h',
        '30m',
        '15m',
        '5m',
        '1m'
    ]

    secs = [
        86400,
        43200,
        28800,
        14400,
        3600,
        1800,
        900,
        300,
        60,
    ]

    def test_init(self):
        day1 = Period('1d')
        day2 = Period(86400)
        day3 = Period(self.one_day)
        self.assertEqual(day1, day2)
        self.assertEqual(day1, day3)

    def test_label(self):
        for label in self.labels:
            period = Period(label)
            self.assertEqual(period.label, label)

    def test_sec(self):
        for sec in self.secs:
            period = Period(sec)
            self.assertEqual(period.sec, sec)

    def test_label_from_sec(self):
        length = len(self.labels)
        for i in range(length):
            period = Period(self.labels[i])
            self.assertEqual(period.sec, self.secs[i])

    def test_sec_from_label(self):
        length = len(self.secs)
        for i in range(length):
            period = Period(self.secs[i])
            self.assertEqual(period.label, self.labels[i])

if __name__ == '__main__':
    unittest.main()
