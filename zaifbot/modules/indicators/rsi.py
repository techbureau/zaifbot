import time
import pandas as pd
from zaifbot.modules.api.wrapper import BotPublicApi


def get_rsi(currency_pair, period='1d', count=5, length=14, to_epoch_time=int(time.time())):
    public_api = BotPublicApi()
    second_api_params = {'period': period, 'count': count + length, 'to_epoch_time': to_epoch_time}
    price_infos = pd.DataFrame(public_api.everything('ohlc_data', currency_pair, second_api_params))
    return _get_rsi(price_infos[['close', 'time']], count, length)


def _get_rsi(price_infos, count, length):
    def _calc_first_a_and_b(close):
        decreased_sum, increased_sum, length = 0, 0, len(close)
        for i in range(1, length):
            decreased_sum += abs(min(close.ix[i] - close.ix[i - 1], 0))
            increased_sum += max(close.ix[i] - close.ix[i - 1], 0)
        return increased_sum / length, decreased_sum / length

    def _generate_next_ab(a, b, length):
        a, b, = a, b
        while True:
            diff = yield a, b
            a = _calc_next_ab(a, max(diff, 0), length)
            b = _calc_next_ab(b, abs(min(diff, 0)), length)

    def _rsi_formula(a, b):
        return a / (a + b) * 100

    def _calc_next_ab(before, diff, length):
        return (before * (length - 1) + diff) / length

    def _create_dict(t, rsi):
        return {'timestamp': t, 'rsi': rsi}

    results = []
    closes = price_infos['close']
    times = price_infos['time']

    # 1本目のRSIの計算
    a_1, b_1 = _calc_first_a_and_b(closes.ix[:length])
    t_1 = times.ix[length]
    results.append(_create_dict(t_1, _rsi_formula(a_1, b_1)))

    # 2本目以降のRSIの計算
    generator = _generate_next_ab(a_1, b_1, length)
    next(generator)
    for i in range(count - 1):
        diff = closes.ix[length + i + 1] - closes.ix[length + i]
        t_i = times.ix[length + i + 1]
        a_i, b_i = generator.send(diff)
        rsi = _rsi_formula(a_i, b_i)
        results.append(_create_dict(t_i, rsi))
    return {'success': 1, 'return': {'RSIs': results}}

