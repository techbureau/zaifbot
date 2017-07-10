from zaifbot.rules.entry import Entry


class SellHigherEntry(Entry):
    def __init__(self, amount, sell_price):
        super().__init__(amount=amount, action='ask')
        self.sell_price = sell_price

    def can_entry(self):
        return self.currency_pair.last_price() > self.sell_price
