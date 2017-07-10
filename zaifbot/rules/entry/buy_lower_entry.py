from zaifbot.rules.entry import Entry


class BuyLowerEntry(Entry):
    def __init__(self, amount, buy_price):
        super().__init__(amount=amount, action='bid')
        self.buy_price = buy_price

    def can_entry(self):
        return self.currency_pair.last_price() < self.buy_price
