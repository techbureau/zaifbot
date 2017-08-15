import itertools
from zaifbot.utils.observer import Observer
from collections import OrderedDict
from threading import Thread


class _AliveObserverMixIn(Observer):
    def update(self, strategy):
        self._remove(strategy.id_)

    def _remove(self, id_):
        raise NotImplementedError


class Portfolio(_AliveObserverMixIn):
    def __init__(self):
        self._strategies = dict()

    def register_strategies(self, strategy, *strategies):
        for strategy in itertools.chain((strategy,), strategies):
            self._strategies[strategy.id_] = dict()
            self._strategies[strategy.id_]['strategy'] = strategy
            strategy.register_observers(self)

    def start(self, *, sec_wait=1):
        strategies = self._gather_strategies()

        for strategy in strategies:
            thread = Thread(target=strategy.start,
                            kwargs={'sec_wait': sec_wait},
                            daemon=True)
            thread.start()
            self._strategies[strategy.id_]['thread'] = thread

    def index(self):
        info_list = list()
        count = 0
        profit = 0
        index = OrderedDict()

        for strategy in self._gather_strategies():
            info = strategy.get_info()
            info_list.append(info)
            count += info['trade_count']
            profit += info['profit']

        index['running_strategies'] = info_list
        index['total_trade_count'] = count
        index['total_profit'] = profit
        return index

    def show(self, id_):
        strategy = self._find_strategy(id_)
        if strategy:
            return strategy.get_info()
        return dict()

    def suspend(self):
        pass

    def stop(self):
        pass

    def _remove(self, id_):
        if id_ in self._strategies:
            del self._strategies[id_]

    def _find_strategy(self, id_):
        strategy = self._strategies.get(id_, None)
        if strategy is None:
            return None
        return strategy['strategy']

    def _find_thread(self, id_):
        strategy = self._strategies.get(id_, None)
        if strategy is None:
            return None
        return strategy['thread']

    def _gather_strategies(self):
        return [strategy['strategy'] for strategy in self._strategies.values()]

    def _gather_threads(self):
        return [strategy['thread'] for strategy in self._strategies.values()]
