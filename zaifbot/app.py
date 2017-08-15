from zaifbot.trade.portfolio import Portfolio
from flask import Flask, request
from zaifbot.web.resources import strategies


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


class ZaifBot(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.portfolio = Portfolio()

    def register_strategies(self, strategy, *strategies):
        self.portfolio.register_strategies(strategy, *strategies)

    def start(self, *, sec_wait=1, host=None, port=None, debug=None, **options):
        self.portfolio.start(sec_wait=sec_wait)
        super().run(host, port, debug, **options)


def zaifbot(import_name):
    app = ZaifBot(import_name)
    app.config['JSON_SORT_KEYS'] = False

    resources = [strategies.resource]
    for resource in resources:
        app.register_blueprint(resource)

    @app.route('/shutdown', methods=['GET'])
    def shutdown():
        shutdown_server()
        return 'true'

    return app
