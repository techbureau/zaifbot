from zaifbot.trade_tools.last_price import last_price
from zaifbot.rules.entry import Entry


class BuyLowerEntry(Entry):
    def __init__(self, amount, buy_price, *, mode='normal'):
        super().__init__(amount=amount, action='bid', mode=mode)
        self.buy_price = buy_price

    def can_entry(self):
        return last_price(self.currency_pair) < self.buy_price
