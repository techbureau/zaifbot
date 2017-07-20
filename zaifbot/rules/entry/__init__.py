from zaifbot.rules.rule import Rule
from zaifbot.trade.trade import Trade
from zaifbot.exchange.action import Action


class Entry(Rule):
    def __init__(self, amount, action='bid'):
        self.currency_pair = None
        self._amount = amount
        self._action = Action(action)

    def can_entry(self, *args, **kwargs):
        raise NotImplementedError

    def entry(self):
        trade = Trade()
        trade.entry(currency_pair=self.currency_pair,
                    amount=self._amount,
                    action=self._action)

        return trade
