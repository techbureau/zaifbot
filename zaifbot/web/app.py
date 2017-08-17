from zaifbot.trade.portfolio import Portfolio
from flask import Flask


class ZaifBot(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.portfolio = Portfolio()

    def register_strategies(self, strategy, *strategies):
        self.portfolio.register_strategies(strategy, *strategies)

    def start(self, *, sec_wait=1, host=None, port=None, debug=None, **options):
        self.portfolio.start(sec_wait=sec_wait)
        self.run(host, port, debug, **options)
