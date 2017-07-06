from zaifbot.rules.rule import Rule
from abc import ABCMeta, abstractmethod


class Exit(Rule, metaclass=ABCMeta):
    def __init__(self, trade_api):
        self._trade_api = trade_api

    @abstractmethod
    def can_exit(self, trade):
        raise NotImplementedError

    def exit(self, trade):
        pass


