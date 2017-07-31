import unittest
from zaifbot.exchange.action import Action, Buy, Sell


class TestAction(unittest.TestCase):
    def test_buy(self):
        buy = Action('bid')
        self.assertEqual(buy, Buy)

    def test_sell(self):
        sell = Action('ask')
        self.assertEqual(sell, Sell)

    def test_name(self):
        self.assertEqual('bid', Buy.name)
        self.assertEqual('ask', Sell.name)

    def test_str(self):
        self.assertEqual('bid', str(Buy))

    def test_opposite(self):
        self.assertEqual(Buy, Sell.opposite_action())

    def test_init_from_action(self):
        buy = Action(Buy)
        self.assertEqual(buy, Buy)

    def test_illegal_arg(self):
        self.assertRaises(ValueError, Action, 'eating')


if __name__ == '__main__':
    unittest.main()
