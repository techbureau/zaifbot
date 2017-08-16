import itertools
from threading import Thread


class Portfolio:
    def __init__(self):
        self._strategies = dict()

    def register_strategies(self, strategy, *strategies):
        for strategy in itertools.chain((strategy,), strategies):
            self._strategies[strategy.id_] = dict()
            self._strategies[strategy.id_]['strategy'] = strategy

    def start(self, *, sec_wait=1):
        strategies = self.collect_strategies()

        for strategy in strategies:
            thread = Thread(target=strategy.start,
                            kwargs={'sec_wait': sec_wait},
                            daemon=True)
            thread.start()
            self._strategies[strategy.id_]['thread'] = thread

    def find_strategy(self, id_):
        strategy = self._strategies.get(id_, None)
        if strategy is None:
            return None
        return strategy['strategy']

    def find_thread(self, id_):
        strategy = self._strategies.get(id_, None)
        if strategy is None:
            return None
        return strategy['thread']

    def collect_strategies(self):
        return [strategy['strategy'] for strategy in self._strategies.values()]

    def collect_threads(self):
        return [strategy['thread'] for strategy in self._strategies.values()]

