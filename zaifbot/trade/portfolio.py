import itertools
from collections import OrderedDict
from threading import Thread


class Portfolio:
    def __init__(self):
        self._strategies = []
        self._running_threads = dict()
        self._progress = _TradesProgress()

    def register_strategies(self, strategy, *strategies):
        for strategy in itertools.chain((strategy,), strategies):
            self._strategies.append(strategy)

    def start(self, *, sec_wait=1):
        for strategy in self._strategies:
            trade_thread = Thread(target=strategy.start,
                                  kwargs={'sec_wait': sec_wait},
                                  daemon=True)
            trade_thread.start()
            self._running_threads[strategy] = trade_thread

    def get_progress(self):
        return self._progress(self._running_threads)


class _TradesProgress:
    def __init__(self):
        self._progress = OrderedDict()

    def __call__(self, running_threads):
        aggregated = self._aggregate_strategies_progress(running_threads)
        self._progress['running_strategies'] = aggregated['info']
        self._progress['total_trade_count'] = aggregated['count']
        self._progress['total_profit'] = aggregated['profit']
        return self._progress

    @staticmethod
    def _aggregate_strategies_progress(running_threads):
        info_list = list()
        count = 0
        profit = 0

        for running_strategy in running_threads.keys():
            info = running_strategy.get_info()
            info_list.append(info)

            count += info['trade_count']
            profit += info['profit']
        return {'count': count, 'profit': profit, 'info': info_list}
