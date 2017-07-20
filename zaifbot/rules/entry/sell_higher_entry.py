from zaifbot.trade.tools import last_price
from zaifbot.rules.entry import Entry


class SellHigherEntry(Entry):
    def __init__(self, currency_pair, amount, sell_price):
        super().__init__(currency_pair=currency_pair, amount=amount, action='ask')
        self.sell_price = sell_price

    def can_entry(self):
        return last_price(self._currency_pair) > self.sell_price
