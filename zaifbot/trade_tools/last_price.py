from zaifbot.exchange.candle_sticks import CandleSticks
from zaifbot.exchange.latest_price import get_latest_price


def last_price(currency_pair, *, timestamp=None):
    if timestamp is None:
        return get_latest_price(currency_pair)

    candle_sticks = CandleSticks(currency_pair, '1m')
    return candle_sticks.last_price(timestamp)
