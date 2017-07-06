from zaifbot.rules.rule import Rule
from abc import ABCMeta, abstractmethod


class Exit(Rule, metaclass=ABCMeta):
    @abstractmethod
    def can_exit(self, trade):
        raise NotImplementedError

    @abstractmethod
    def exit(self, trade_api, trade):
        raise NotImplementedError

