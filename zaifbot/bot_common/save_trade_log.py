from json import dumps
import os


def save_trade_log(filename, time, action, price, amount, limit=None):
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
    target_dir = os.path.join(parent_dir, 'bot_common')
    filepath = os.path.join(target_dir, filename)

    trade_log = {
        'time': time,
        'action': action,
        'price': price,
        'amount': amount,
        'limit': limit
    }
    f = open(filepath, 'a')
    trade_str = dumps(trade_log)
    f.write(trade_str + '\n')
    f.close()
