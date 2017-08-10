from zaifbot.trade.tools import last_price
from zaifbot.rules.exit.base import Exit


class SellHigherExit(Exit):
    def __init__(self, exit_price, name=None):
        super().__init__(name=name)
        self._exit_price = exit_price

    def can_exit(self, trade):
        return self._exit_price < last_price(trade.currency_pair)
