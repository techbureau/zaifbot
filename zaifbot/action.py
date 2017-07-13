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
            return self._action == other._action
        if isinstance(other, str):
            return self._action == other
        return False


class _Buy(_TradeAction):
    @staticmethod
    def is_my_action(action):
        return action == 'ask'

    @staticmethod
    def opposite_action():
        return Action('bid')


class _Sell(_TradeAction):
    @staticmethod
    def is_my_action(action):
        return action == 'bid'

    @staticmethod
    def opposite_action():
        return Action('ask')


Sell = Action('ask')
Buy = Action('bid')