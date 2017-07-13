from zaifbot.exchange.currency_pairs import CurrencyPair
from zaifbot.exchange.api.websocket import BotStreamApi
from zaifbot.exchange.api.http import BotPublicApi


def get_latest_price(currency_pair):
    currency_pair = CurrencyPair(currency_pair)

    if currency_pair.is_token:
        public_api = BotPublicApi()
        return public_api.last_price(currency_pair)['last_price']
    else:
        stream_api = BotStreamApi()
        return stream_api.execute(currency_pair)['last_price']['price']
