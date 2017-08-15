from flask import Blueprint, jsonify
from flask import current_app as app

resource = Blueprint('strategies', __name__, url_prefix='/strategies')


@resource.route('/', methods=['GET'])
def index():
    return jsonify(app.portfolio.index())


@resource.route('/<id_>', methods=['GET'])
def show(id_):
    return jsonify(app.portfolio.show(id_))
