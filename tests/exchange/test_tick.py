import unittest
from zaifbot.exchange import Tick, CurrencyPair


class TestTick(unittest.TestCase):
    def setUp(self):
        self._btc_jpy = CurrencyPair('btc_jpy')
        self._xem_jpy = CurrencyPair('xem_jpy')
        self._xem_btc = CurrencyPair('xem_btc')
        self._zaif_jpy = CurrencyPair('zaif_jpy')
        self._zaif_btc = CurrencyPair('zaif_btc')

    def test_btc_jpy(self):
        tick = Tick(self._btc_jpy)
        case1 = tick.truncate_price(100)
        case2 = tick.truncate_price(3)
        case3 = tick.truncate_price(5)
        case4 = tick.truncate_price(5.0)
        case5 = tick.truncate_price(123.45678)

        cases = (case1, case2, case3, case4, case5)
        expected_values = (100, 0, 5, 5, 120)
        self.assertEqual(cases, expected_values)

    def test_xem_jpy(self):
        tick = Tick(self._xem_jpy)
        case1 = tick.truncate_price(0.1)
        case2 = tick.truncate_price(1)
        case3 = tick.truncate_price(1.0)
        case4 = tick.truncate_price(0.000001)
        case5 = tick.truncate_price(0.12345)

        cases = (case1, case2, case3, case4, case5)
        expected_values = (0.1, 1.0, 1.0, 0.0, 0.1234)
        self.assertEqual(cases, expected_values)

    def test_zaif_jpy(self):
        tick = Tick(self._zaif_jpy)
        case1 = tick.truncate_price(0.1)
        case2 = tick.truncate_price(1)
        case3 = tick.truncate_price(1.0)
        case4 = tick.truncate_price(0.000001)
        case5 = tick.truncate_price(0.123456)

        cases = (case1, case2, case3, case4, case5)
        expected_values = (0.1, 1.0, 1.0, 0.0, 0.1234)
        self.assertEqual(cases, expected_values)

    def test_xem_btc(self):
        tick = Tick(self._xem_btc)
        case1 = tick.truncate_price(0.00000001)
        case2 = tick.truncate_price(0.00000001234)
        case3 = tick.truncate_price(0.00000341)
        case4 = tick.truncate_price(1)

        cases = (case1, case2, case3, case4)
        expected_values = (0.00000001, 0.00000001, 0.00000341, 1.0)
        self.assertEqual(cases, expected_values)

    def test_zaif_btc(self):
        tick = Tick(self._zaif_btc)
        case1 = tick.truncate_price(0.00000001)
        case2 = tick.truncate_price(0.00000001234)
        case3 = tick.truncate_price(0.00000341)
        case4 = tick.truncate_price(1)

        cases = (case1, case2, case3, case4)
        expected_values = (0.00000001, 0.00000001, 0.00000341, 1.0)
        self.assertEqual(cases, expected_values)


if __name__ == '__main__':
    unittest.main()
