import unittest
from zaifbot.exchange import CurrencyPair


class TestCurrencyPair(unittest.TestCase):
    def setUp(self):
        self._btc_jpy = CurrencyPair('btc_jpy')
        self._zaif_jpy = CurrencyPair('zaif_jpy')

    def test_is_same_object(self):
        btc_jpy = CurrencyPair('btc_jpy')
        self.assertIs(btc_jpy, self._btc_jpy)

    def test_name(self):
        expected = 'btc_jpy'
        self.assertEqual(expected, self._btc_jpy.name)

    def test_is_token(self):
        self.assertIs(self._btc_jpy.is_token, False)
        self.assertIs(self._zaif_jpy.is_token, True)

    def test_info(self):
        pass

    def test_init_from_currency_pair_obj(self):
        btc_jpy = CurrencyPair(self._btc_jpy)
        self.assertIs(btc_jpy, self._btc_jpy)

    def test_str(self):
        expected = 'btc_jpy'
        self.assertEqual(expected, str(self._btc_jpy))

if __name__ == '__main__':
    unittest.main()
