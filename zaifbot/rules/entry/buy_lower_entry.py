from zaifbot.rules.entry import Entry


class BuyLowerEntry(Entry):
    def __init__(self, currency_pair, amount, api, buy_price):
        super().__init__(currency_pair=currency_pair, amount=amount, api=api, action='bid')
        self._buy_price = buy_price

    def can_entry(self):
        return self._currency_pair.last_price() < self._buy_price
