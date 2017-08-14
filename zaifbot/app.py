import itertools
from collections import OrderedDict
from flask import Flask, jsonify
from threading import Thread


class Portfolio:
    def __init__(self):
        self._strategies = []
        self._running_threads = dict()
        self._progress = _TradingProgress()

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
        return self._progress.get_progress(self._running_threads)


class _TradingProgress:
    def __init__(self):
        self._progress = OrderedDict()
        self._total_profit = 0
        self._total_trade_count = 0
        self._strategies_info = OrderedDict()

    def get_progress(self, running_threads):
        self._progress['running_strategies'] = self._aggregate_strategies_progress(running_threads)
        self._progress['total_trade_count'] = self._total_trade_count
        self._progress['total_profit'] = self._total_profit
        return self._progress

    def _aggregate_strategies_progress(self, running_threads):
        progresses = list()

        for running_strategy in running_threads.keys():
            info = running_strategy.get_info()
            progresses.append(info)

            self._add_trade_count(info['trade_count'])
            self._add_profit(info['profit'])
        return progresses

    def _add_trade_count(self, count):
        self._total_trade_count += count

    def _add_profit(self, profit):
        self._total_profit += profit


class ZaifBot(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.portfolio = Portfolio()

    def register_strategies(self, strategy, *strategies):
        self.portfolio.register_strategies(strategy, *strategies)

    def start(self, *, sec_wait=1, host=None, port=None, debug=None, **options):
        self.portfolio.start(sec_wait=sec_wait)
        # stop server when all thread is gone
        # stop all thread when server has some problem
        super().run(host, port, debug, **options)


def zaifbot(import_name):
    app = ZaifBot(import_name)
    app.config['JSON_SORT_KEYS'] = False

    @app.route('/', methods=['GET'])
    def info():
        res = jsonify(app.portfolio.get_progress())
        return res

    return app
