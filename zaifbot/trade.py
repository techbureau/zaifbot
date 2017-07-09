from zaifbot.common.action import Action
from datetime import datetime


class Trade:
    def __init__(self, currency_pair, entry_price, amount, action):
        self.currency_pair = currency_pair
        self.entry_datetime = datetime.now()
        self.entry_price = entry_price
        self.amount = amount
        self.action = Action(action)
        self.exit_price = None
        self.exit_datetime = None

    def profit(self):
        pass

    def save(self):
        """DBに保存"""
        pass

    def update(self):
        """execute時"""
        pass
