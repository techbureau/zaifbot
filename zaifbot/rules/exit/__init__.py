from zaifbot.rules.rule import Rule
from abc import ABCMeta, abstractmethod


class Exit(Rule, metaclass=ABCMeta):
    def __init__(self):
        self.trade_api = None

    @abstractmethod
    def can_exit(self, trade):
        raise NotImplementedError

    def exit(self, trade):
        pass


