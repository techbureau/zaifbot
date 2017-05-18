import time
from pandas import DataFrame
from zaifbot.modules.api.wrapper import BotPublicApi


def get_rsi(currency_pair, period='1d', count=5, length=14, to_epoch_time=int(time.time())):
    public_api = BotPublicApi()
    second_api_params = {'period': period, 'count': count + length, 'to_epoch_time': to_epoch_time}
    infos = DataFrame(public_api.everything('ohlc_data', currency_pair, second_api_params))
    return _get_rsi(infos[['close', 'time']], count, length)


def _get_rsi(df, count, length):
    results = []
    a_1, b_1 = _calc_first_a_and_b(df.ix[:length, 'close'])
    t_1 = df.ix[length, 'time']
    results.append(_create_dict(t_1, _rsi_formula(a_1, b_1)))

    generator = _generate_next_a_and_b(a_1, b_1, length)
    next(generator)

    for i in range(count - 1):
        diff = df.ix[length + i + 1, 'close'] - df.ix[length + i, 'close']
        t_i = df.ix[length + i + 1, 'time']
        a_i, b_i = generator.send(diff)
        rsi = _rsi_formula(a_i, b_i)
        results.append(_create_dict(t_i, rsi))
    return {'success': 1, 'return': {'rsis': results}}


def _calc_first_a_and_b(close):
    decreased_sum, increased_sum, length = 0, 0, len(close)
    for i in range(1, length):
        decreased_sum += min(close.ix[i] - close.ix[i - 1], 0) * (-1)
        increased_sum += max(close.ix[i] - close.ix[i - 1], 0)
    return increased_sum / length, decreased_sum / length


def _generate_next_a_and_b(a, b, length):
    a, b,  = a, b
    while True:
        diff = yield a, b
        a = _next_rsi_formula(a, max(diff, 0), length)
        b = _next_rsi_formula(b, min(diff, 0) * (-1), length)


def _rsi_formula(a, b):
    return a / (a + b) * 100


def _next_rsi_formula(before, diff, length):
    return (before * (length - 1) + diff) / length


def _create_dict(t, rsi):
    return {'timestamp': t, 'rsi': rsi}
