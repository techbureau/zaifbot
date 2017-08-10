from flask import Flask
from multiprocessing import Process, Manager, Lock


class ZaifBot(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self._strategies = []
        self._process_info = Manager().dict()
        self._lock = Lock()

    def register_strategy(self, strategy):
        self._strategies.append(strategy)

    def start(self, host=None, port=None, debug=None, **options):
        for strategy in self._strategies:
            p = Process(target=strategy.start, args=(self.process_info,))
            p.daemon = True
            p.start()

        super().run(host, port, debug, **options)

    @property
    def process_info(self):
        with self._lock:
            return self._process_info

    def update_process_info(self, key, value):
        with self._lock:
            self._process_info[key] = value

app = ZaifBot(__name__)


@app.route('/', methods=['GET'])
def info():
    return app.process_info

if __name__ == '__main__':
    app.register_strategy()
    app.run()
