from zaifbot.rules.rule import Rule
from zaifbot.trade.trade import Trade
from zaifbot.exchange.action import Action
from zaifbot.trade.tools import last_price


class Entry(Rule):
    def __init__(self, amount, action='bid'):
        self.currency_pair = None
        self._amount = amount
        self._action = Action(action)

    def can_entry(self, *args, **kwargs):
        raise NotImplementedError

    def entry(self, trade_api):
        price = last_price(currency_pair=self.currency_pair)
        trade_api.trade(currency_pair=self.currency_pair,
                        amount=self._amount,
                        price=price,
                        action=self._action)
        trade = Trade()
        trade.entry(currency_pair=self.currency_pair,
                    amount=self._amount,
                    entry_price=price,
                    action=self._action)

        return trade
