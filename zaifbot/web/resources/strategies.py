from flask import Blueprint, jsonify
from flask import current_app as app


resource = Blueprint('strategies', __name__, url_prefix='/strategies')


@resource.route('/', methods=['GET'])
def index():
    return jsonify(app.portfolio.get_progress())
