import unittest
from zaifbot.exchange import Period


class TestPeriod(unittest.TestCase):
    one_day = Period('1d')
    labels = [
        '1d',
        '8h',
        '4h',
        '1h',
        '30m',
        '15m',
        '5m',
        '1m'
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
            self.assertEqual(period.get_label(), label)

    def test_sec(self):
        pass


if __name__ == '__main__':
    unittest.main()
