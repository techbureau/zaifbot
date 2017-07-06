from zaifbot.rules.rule import Rule
from abc import ABCMeta, abstractmethod
from zaifbot.common.bot_const import Action
from zaifbot.trade import Trade


class Entry(Rule, metaclass=ABCMeta):
    def __init__(self, currency_pair, amount, api, action='bid'):
        self._currency_pair = currency_pair
        self._amount = amount
        self._api = api
        self._action = Action(action)

    @abstractmethod
    def can_entry(self):
        raise NotImplementedError

    def entry(self):
        price = self._currency_pair.last_price()
        self._api.trade(currency_pair=self._currency_pair,
                        amount=self._amount,
                        price=price,
                        action=self._action)

        trade = Trade(currency_pair=self._currency_pair,
                      amount=self._amount,
                      entry_price=price,
                      action=self._action)

        trade.save()
        return trade
