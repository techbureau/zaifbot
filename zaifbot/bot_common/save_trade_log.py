from json import dumps
from time import time


class TradeHistory:
    def __init__(self):
        timestamp = int(time())
        self._filename = "./trade_history" + str(timestamp) + ".log"

    def save_trade_log(self, trade_log):
        f = open(self._filename, 'a')
        trade_str = dumps(trade_log)
        f.write(trade_str + '\n')
        f.close()
