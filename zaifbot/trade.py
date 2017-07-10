from datetime import datetime
from zaifbot.common.action import Action
from zaifbot.dao.base import TradesDao


class Trade:
    def __init__(self, currency_pair, entry_price, amount, action):
        self.currency_pair = currency_pair
        self.entry_datetime = datetime.now()
        self.entry_price = entry_price
        self.amount = amount
        self.action = Action(action)
        self.exit_price = None
        self.exit_datetime = None
        self._dao = TradesDao

    def profit(self):
        pass

    def save(self):
        self._dao.create(
            currency_pair=str(self.currency_pair),
            amount=self.amount,
            entry_price=self.entry_price,
            action=str(self.action)
        )
        return self

    def update(self):
        """execute時"""
        pass
