from zaifbot.api_management import APIRepository
from zaifbot.rules.rule import Rule
from zaifbot.trade import Trade
from zaifbot.exchange.action import Action


class Entry(Rule):
    def __init__(self, amount, action='bid'):
        self.currency_pair = None
        self._trade_api = APIRepository().trade_api
        self._amount = amount
        self._action = Action(action)

    def can_entry(self, *args, **kwargs):
        raise NotImplementedError

    def entry(self):
        price = self.currency_pair.last_price()
        self._trade_api.trade(currency_pair=self.currency_pair,
                              amount=self._amount,
                              price=price,
                              action=self._action)
        trade = Trade()
        trade.entry(currency_pair=self.currency_pair,
                    amount=self._amount,
                    entry_price=price,
                    action=self._action)

        return trade
