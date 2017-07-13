from zaifbot.exchange.latest_price import latest_closing_price
from zaifbot.rules.entry import Entry


class BuyLowerEntry(Entry):
    def __init__(self, amount, buy_price):
        super().__init__(amount=amount, action='bid')
        self.buy_price = buy_price

    def can_entry(self):
        return latest_closing_price(self.currency_pair) < self.buy_price
