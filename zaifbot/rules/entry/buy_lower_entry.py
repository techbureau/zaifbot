from zaifbot.exchange.latest_price import get_latest_price
from zaifbot.rules.entry import Entry


class BuyLowerEntry(Entry):
    def __init__(self, amount, buy_price):
        super().__init__(amount=amount, action='bid')
        self.buy_price = buy_price

    def can_entry(self):
        return get_latest_price(self.currency_pair) < self.buy_price
