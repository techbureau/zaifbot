import unittest
from zaifbot.trade.trade import Trade


class TestTrade(unittest.TestCase):
    def setUp(self):
        self._trade = Trade()
        self._trade2 = Trade()

    def test_is_long(self):
        self._trade.action = 'bid'
        self._trade2.action = 'ask'

        results = (self._trade.is_long, self._trade2.is_long)
        expected = (True, False)
        self.assertEqual(results, expected)

    def test_is_short(self):
        self._trade.action = 'bid'
        self._trade2.action = 'ask'
        results = (self._trade.is_short, self._trade2.is_short)
        expected = (False, True)
        self.assertEqual(results, expected)

    def test_is_closed(self):
        self._trade.closed = True
        self._trade2.closed = False
        results = (self._trade.is_closed, self._trade2.is_closed)
        expected = (True, False)
        self.assertEqual(results, expected)

    def test_profit(self):
        self._trade.action = 'bid'
        self._trade.entry_price = 100
        self._trade.exit_price = 200

        self._trade2.action = 'ask'
        self._trade2.entry_price = 100
        self._trade2.exit_price = 200

        results = (self._trade.profit(), self._trade2.profit())
        expected = (100, -100)
        self.assertEqual(results, expected)


if __name__ == '__main__':
    unittest.main()
