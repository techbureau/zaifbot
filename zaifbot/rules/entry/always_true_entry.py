from zaifbot.rules.entry.base import Entry


class AlwaysTrueEntry(Entry):
    def __init__(self, currency_pair, amount, action, name=None):
        super().__init__(currency_pair=currency_pair, amount=amount, action=action, name=name)

    def can_entry(self):
        return True
