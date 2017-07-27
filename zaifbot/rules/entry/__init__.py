from zaifbot.rules.rule import Rule
from zaifbot.trade.trade import Trade
from zaifbot.exchange.action import Action
from zaifbot.exchange.currency_pairs import CurrencyPair


class Entry(Rule):
    def __init__(self, currency_pair, amount, action='bid'):
        self._currency_pair = CurrencyPair(currency_pair)
        self._amount = amount
        self._action = Action(action)

    def can_entry(self, *args, **kwargs):
        raise NotImplementedError

    def entry(self):
        trade = self._create_new_trade()
        trade.entry(currency_pair=self._currency_pair,
                    amount=self._amount,
                    action=self._action)

        return trade

    @staticmethod
    def _create_new_trade():
        return Trade()
