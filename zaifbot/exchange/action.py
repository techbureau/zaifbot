from abc import ABCMeta, abstractclassmethod


def Action(action):
    for cls in _TradeAction.__subclasses__():
        if isinstance(action, str):
            if cls.is_my_action(action):
                return cls(action)
            continue

        if isinstance(action, _TradeAction):
            return action

    raise ValueError('illegal argument')


class _TradeAction(metaclass=ABCMeta):
    def __init__(self, action):  # necessary
        self._name = self.name

    def __str__(self):
        return self._name

    def __eq__(self, other):
        if isinstance(other, _TradeAction):
            return self._name == other._name
        if isinstance(other, str):
            return self._name == other
        return False

    @property
    @abstractclassmethod
    def name(self):
        raise NotImplementedError

    @abstractclassmethod
    def is_my_action(self):
        raise NotImplementedError


class _Buy(_TradeAction):
    @staticmethod
    def is_my_action(action):
        return action == 'bid'

    @staticmethod
    def opposite_action():
        return Action('ask')

    @property
    def name(self):
        return 'bid'


class _Sell(_TradeAction):
    @staticmethod
    def is_my_action(action):
        return action == 'ask'

    @staticmethod
    def opposite_action():
        return Action('bid')

    @property
    def name(self):
        return 'ask'


Sell = Action('ask')
Buy = Action('bid')
