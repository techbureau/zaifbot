import itertools
from zaifbot.utils.observer import Observer
from collections import OrderedDict
from threading import Thread


class _AliveObserverMixIn(Observer):
    def update(self, strategy):
        self.delete(strategy)

    def delete(self, strategy):
        raise NotImplementedError


class Portfolio(_AliveObserverMixIn):
    def __init__(self):
        self._strategies = dict()
        self._running_threads = dict()

    def register_strategies(self, strategy, *strategies):
        for strategy in itertools.chain((strategy,), strategies):
            self._strategies[strategy.id_] = strategy
            strategy.register_observers(self)

    def start(self, *, sec_wait=1):
        for strategy in self._strategies.values():
            trade_thread = Thread(target=strategy.start,
                                  kwargs={'sec_wait': sec_wait},
                                  daemon=True)
            trade_thread.start()
            self._running_threads[strategy] = trade_thread

    def index(self):
        info_list = list()
        count = 0
        profit = 0
        portfolio = OrderedDict()

        for running_strategy in self._running_threads.keys():
            info = running_strategy.get_info()
            info_list.append(info)

            count += info['trade_count']
            profit += info['profit']

        portfolio['running_strategies'] = info_list
        portfolio['total_trade_count'] = count
        portfolio['total_profit'] = profit
        return portfolio

    def show(self, id_):
        strategy = self._find(id_)
        if strategy:
            return strategy.get_info()
        return dict()

    def suspend(self):
        pass

    def stop(self):
        pass

    def delete(self, id_):
        if id_ in self._running_threads.keys():
            strategy = self._find(id_)
            del self._running_threads[strategy]

    def _find(self, id_):
        return self._strategies.get(id_, None)