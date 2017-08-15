from flask import jsonify, redirect
from zaifbot.web.app import ZaifBot
from zaifbot.web.resources import strategies
from zaifbot.errors import ZaifBotError, InvalidRequest


__version__ = '0.0.6'


def zaifbot(import_name):
    app = ZaifBot(import_name)
    app.config['JSON_SORT_KEYS'] = False

    @app.errorhandler(InvalidRequest)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    resources = [strategies.resource]
    for resource in resources:
        app.register_blueprint(resource)

    @app.route('/')
    def root():
        return redirect('/strategies/', code=303)

    return app
