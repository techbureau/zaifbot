from flask import jsonify, redirect
from zaifbot.web.app import ZaifBot
from zaifbot.web.resources import strategies
from zaifbot.errors import ZaifBotError, InvalidRequest


__version__ = '0.0.6'


def zaifbot(import_name):
    app = ZaifBot(import_name)
    app.url_map.strict_slashes = False
    app.config['JSON_SORT_KEYS'] = False

    _customize_flask_logger()

    @app.errorhandler(InvalidRequest)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.route('/')
    def root():
        return redirect('/strategies/', code=303)

    resources = [strategies.resource]
    for resource in resources:
        app.register_blueprint(resource)

    return app


def _customize_flask_logger():
    import logging
    from zaifbot.logger import bot_logger, bot_file_handler, bot_console_handler
    logger = logging.getLogger('werkzeug')
    logger.name = 'Web'
    logger.setLevel(logging.INFO)

    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)

    logger.addHandler(bot_console_handler)
    logger.addHandler(bot_file_handler)
