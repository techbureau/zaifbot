from flask import Flask
from zaifbot.utils.observer import Observer
from multiprocessing import Process, Lock


class ZaifBot(Flask, Observer):
    def __init__(self, import_name):
        super().__init__(import_name)
        self._strategies = []
        self._process_info = dict()
        self._lock = Lock()

    def register_strategy(self, strategy):
        self._strategies.append(strategy)

    def start(self, host=None, port=None, debug=None, **options):
        for strategy in self._strategies:
            strategy.register_observers(self)

            p = Process(target=strategy.start, args=(self._process_info,))
            p.daemon = True
            p.start()

        super().run(host, port, debug, **options)

    @property
    def process_info(self):
        with self._lock:
            return self._process_info

    def update(self, strategy, *args, **kwargs):
        with self._lock:
            pass

app = ZaifBot(__name__)


@app.route('/', methods=['GET'])
def info():
    return app._process_info

if __name__ == '__main__':
    app.register_strategy()
    app.run()
