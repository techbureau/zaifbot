def Action(action):
    for cls in _TradeAction.__subclasses__():
        if cls.is_my_action(action):
            return cls(action)
    raise ValueError


class _TradeAction:
    def __init__(self, action):
        self._action = action

    def __str__(self):
        return self._action

    def __eq__(self, other):
        if isinstance(other, _TradeAction):
            return self._action is other._action
        if isinstance(other, str):
            return self._action is other
        return False


class _Buy(_TradeAction):
    @staticmethod
    def is_my_action(action):
        return action is 'ask'


class _Sell(_TradeAction):
    @staticmethod
    def is_my_action(action):
        return action is 'bid'
