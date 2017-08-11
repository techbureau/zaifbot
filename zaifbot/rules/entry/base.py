from zaifbot.rules.rule import Rule
from zaifbot.exchange.action import Action
from zaifbot.exchange.currency_pairs import CurrencyPair


class Entry(Rule):
    def __init__(self, currency_pair, amount, action='bid', name=None):
        self._currency_pair = CurrencyPair(currency_pair)
        self._amount = amount
        self._action = Action(action)
        self.name = name or self.__class__.__name__

    def can_entry(self, *args, **kwargs):
        raise NotImplementedError

    def entry(self, trade):
        trade.entry(currency_pair=self._currency_pair,
                    amount=self._amount,
                    action=self._action)

        return trade

    # todo: use public property
    @property
    def currency_pair(self):
        return self._currency_pair

    @property
    def action(self):
        return self._action

    @property
    def amount(self):
        return self._amount
