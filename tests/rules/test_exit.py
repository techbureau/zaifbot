import unittest
from unittest.mock import Mock
from zaifbot.rules import Exit


class ExitForTest(Exit):
    def can_exit(self, trade):
        return True

    @staticmethod
    def exit(trade):
        trade.exit()


class TradeForExitTest:
    def exit(self):
        pass


class TestEntry(unittest.TestCase):
    def test_exit(self):
        test_trade = Mock(spec=TradeForExitTest)
        test_exit = ExitForTest()
        test_exit.exit(test_trade)
        test_trade.exit.assert_called_with()

if __name__ == '__main__':
    unittest.main()
