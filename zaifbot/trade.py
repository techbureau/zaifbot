from zaifbot.common.bot_const import Action
from datetime import datetime


class Trade:
    def __init__(self, currency_pair, entry_price, amount, action):
        self.currency_pair = currency_pair
        self.entry_datetime = datetime.now()
        self.amount = amount
        self.entry_price = entry_price
        self.action = Action(action)

    def entry_point(self):
        pass

    def exit_point(self):
        pass

    def profit(self):
        pass

    def save(self):
        pass
