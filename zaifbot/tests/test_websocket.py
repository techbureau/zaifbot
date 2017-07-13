import unittest
from zaifbot.tests import BotTest
from zaifbot.exchange.api.websocket import BotStreamApi


class TestZaifPublicStreamApi(BotTest):
    def test_singletom(self):
        stream_api = BotStreamApi()
        stream_api2 = BotStreamApi()
        self.assertEqual(stream_api, stream_api2)

    def test_get_last_price(self):
        stream_api = BotStreamApi()
        stream_api.execute(currency_pair='btc_jpy')

if __name__ == '__main__':
    unittest.main()