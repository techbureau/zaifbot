import unittest
from unittest.mock import Mock
from zaifbot.rules import Exit


class TradeForExitTest:
    def exit(self):
        pass


class TestEntry(unittest.TestCase):
    def setUp(self):
        self._trade_mock = Mock(spec=TradeForExitTest)
        self._exit = Exit()

    def test_can_exit(self):
        self.assertRaises(NotImplementedError, self._exit.can_exit, self._trade_mock)

    def test_exit(self):
        self._exit.exit(self._trade_mock)
        self._trade_mock.exit.assert_called_with()

    def test_name(self):
        self.assertEqual(self._exit.name, 'Exit')

if __name__ == '__main__':
    unittest.main()
