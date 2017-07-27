import unittest
from unittest.mock import Mock
from zaifbot.rules import Entry


class EntryForTest(Entry):
    def can_entry(self):
        return True


class TradeForTest:
    def entry(self):
        pass


class TestEntry(unittest.TestCase):
    def test_entry(self):
        entry = EntryForTest(currency_pair='btc_jpy',
                             amount=1,
                             action='bid')

        entry._create_new_trade = Mock()
        trade_mock = Mock(spec=TradeForTest)
        entry._create_new_trade.return_value = trade_mock
        entry.entry()

        trade_mock.entry.assert_called_with(
            currency_pair=entry._currency_pair,
            amount=entry._amount,
            action=entry._action
        )

if __name__ == '__main__':
    unittest.main()
