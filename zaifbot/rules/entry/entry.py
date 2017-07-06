from zaifbot.rules.rule import Rule
from abc import ABCMeta, abstractmethod
from zaifbot.common.bot_const import Action


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
        self._api.trade(currency_pair=self._currency_pair,
                        amount=self._amount,
                        price=self._currency_pair.last_price(),
                        action=self._action)
