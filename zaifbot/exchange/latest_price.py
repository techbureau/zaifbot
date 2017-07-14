from zaifbot.exchange.currency_pairs import CurrencyPair
from zaifbot.api_management import APIRepository


def get_latest_price(currency_pair):
    currency_pair = CurrencyPair(currency_pair)

    if currency_pair.is_token:
        public_api = APIRepository().public_api
        # todo: ここがNoneになる。
        print(public_api.last_price(currency_pair)['last_price'])
        return public_api.last_price(currency_pair)['last_price']
    else:
        stream_api = APIRepository().stream_api
        return stream_api.execute(currency_pair)['last_price']['price']
