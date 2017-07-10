import time
from zaifbot.trading_strategy import Strategy
from zaifbot.web import BotTradeApi
from zaifbot.tools import preset_keys
from zaifbot.rules.entry import Entry
from zaifbot.rules.exit import Exit


"""
時間が経ったら売買する取引です。テスト用です。

buy and sell after waiting some time. mainly used for test
"""

preset_keys(key='your_key',
            secret='your_secret')

trade_api = BotTradeApi()


class WaitTimeEntry(Entry):
    def __init__(self, amount, action):
        super().__init__(amount, action)
        self._time = int(time.time())

    def can_entry(self):
        now = int(time.time())
        return now - self._time > 10


class WaitTimeExit(Exit):
    def __init__(self):
        super().__init__()
        self._time = int(time.time())

    def can_exit(self, trade):
        now = int(time.time())
        return now - self._time > 10


entry_rule = WaitTimeEntry(amount=1, action='bid')
exit_rule = WaitTimeExit()

my_strategy = Strategy(currency_pair='zaif_jpy',
                       entry_rule=entry_rule,
                       exit_rule=exit_rule,
                       trade_api=trade_api)

my_strategy.start()
