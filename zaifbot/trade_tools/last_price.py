from zaifbot.exchange.candle_sticks import CandleSticks
from zaifbot.exchange.latest_price import get_latest_price


def last_price(currency_pair, *, timestamp=None):
    if timestamp is None:
        return get_latest_price(currency_pair)

    candle_sticks = CandleSticks(currency_pair, '1m')
    # candle_stick側に実装する。
    return candle_sticks.request_data(count=1, to_epoch_time=timestamp)[0]['close']
