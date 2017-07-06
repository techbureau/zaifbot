from zaifbot.rules.entry import Entry


class SellHigherEntry(Entry):
    def __init__(self, currency_pair, amount, api, sell_price):
        super().__init__(currency_pair=currency_pair, amount=amount, api=api, action='ask')
        self._sell_price = sell_price

    def can_entry(self):
        return self._currency_pair.last_price() > self._sell_price
