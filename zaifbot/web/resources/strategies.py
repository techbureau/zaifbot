from collections import OrderedDict
from flask import Blueprint, jsonify, Response
from flask import current_app as app
from zaifbot.errors import InvalidRequest

resource = Blueprint('strategies', __name__, url_prefix='/strategies')


@resource.route('/', methods=['GET'])
def index():
    strategy_list = list()
    trade_count = 0
    total_profit = 0
    rv = OrderedDict()

    strategies = app.portfolio.collect_strategies()
    for strategy in strategies:
        info = strategy.get_info()
        strategy_list.append(info)
        trade_count += info['trade_count']
        total_profit += info['profit']

    rv['strategies'] = strategy_list
    rv['total_trades'] = trade_count
    rv['total_profit'] = total_profit

    res = jsonify(rv)
    return res


@resource.route('/<id_>', methods=['GET'])
def show(id_):
    strategy = app.portfolio.find_strategy(id_)
    if strategy:
        res = jsonify(strategy.get_info())
        return res
    raise InvalidRequest('strategy not found', status_code=404)


@resource.route('/<id_>', methods=['DELETE'])
def stop(id_):
    strategy = app.portfolio.find_strategy(id_)
    if strategy is None:
        raise InvalidRequest('strategy not found', status_code=404)

    strategy.stop()
    res = Response()
    res.status_code = 204
    return res


@resource.route('/<id_>/suspend', methods=['PATCH'])
def suspend(id_):
    pass
