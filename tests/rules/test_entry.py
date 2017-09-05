import unittest
from unittest.mock import Mock
from zaifbot.rules.entry.base import Entry


class TradeForEntryTest:
    def entry(self):
        pass


class TestEntry(unittest.TestCase):
    def setUp(self):
        self._entry = Entry(
            currency_pair='btc_jpy',
            amount=1,
            action='bid'
        )

    def test_can_entry(self):
        self.assertRaises(NotImplementedError, self._entry.can_entry)

    def test_entry(self):
        trade_mock = Mock(spec=TradeForEntryTest)
        self._entry.entry(trade_mock)

        trade_mock.entry.assert_called_with(
            currency_pair=self._entry.currency_pair,
            amount=self._entry.amount,
            action=self._entry.action,
        )

    def test_name(self):
        self.assertEqual(self._entry.name, 'Entry')

if __name__ == '__main__':
    unittest.main()
