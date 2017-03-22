from json import dumps


def save_trade_log(trade_log):
    f = open('./trade_history.log', 'a')
    trade_str = dumps(trade_log)
    f.write(trade_str + '\n')
    f.close()
