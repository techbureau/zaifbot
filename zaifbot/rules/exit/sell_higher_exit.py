from zaifbot.trade.tools import last_price
from zaifbot.rules.exit import Exit


class SellHigherExit(Exit):
    def __init__(self, exit_price):
        super().__init__()
        self.exit_price = exit_price

    def can_exit(self, trade):
        return self.exit_price > last_price(trade.currency_pair)
