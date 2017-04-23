from json import dumps


def save_trade_log(filename, time, action, price, amount, limit=None):
    trade_log = {
        'time': time,
        'action': action,
        'price': price,
        'amount': amount,
        'limit': limit
    }
    f = open(filename, 'a')
    trade_str = dumps(trade_log)
    f.write(trade_str + '\n')
    f.close()
