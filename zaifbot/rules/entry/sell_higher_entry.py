from zaifbot.exchange.latest_price import get_latest_price
from zaifbot.rules.entry import Entry


class SellHigherEntry(Entry):
    def __init__(self, amount, sell_price):
        super().__init__(amount=amount, action='ask')
        self.sell_price = sell_price

    def can_entry(self):
        return get_latest_price(self.currency_pair) > self.sell_price
