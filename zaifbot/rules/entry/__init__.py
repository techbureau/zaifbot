from zaifbot.rules.rule import Rule
from zaifbot.common.action import Action
from zaifbot.trade import Trade


class Entry(Rule):
    def __init__(self, amount, action='bid'):
        self.currency_pair = None
        self.trade_api = None
        self._amount = amount
        self._action = Action(action)

    def can_entry(self, *args, **kwargs):
        raise NotImplementedError

    def entry(self):
        price = self.currency_pair.last_price()
        self.trade_api.trade(currency_pair=self.currency_pair,
                             amount=self._amount,
                             price=price,
                             action=self._action)

        trade = Trade()
        trade.entry(currency_pair=self.currency_pair,
                    amount=self._amount,
                    entry_price=price,
                    action=self._action)

        return trade
