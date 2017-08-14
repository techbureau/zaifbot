import os
import logging.handlers
from slack_logger import SlackHandler, SlackFormatter


def _bot_console_handler():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('[%(name)s][%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    return console_handler


def _bot_file_handler(file=None):
    if file is None:
        current_dir = os.path.dirname(__file__)
        file = os.path.join(current_dir, 'logs/zaifbot.log')

    file_handler = logging.handlers.TimedRotatingFileHandler(filename=file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('[%(asctime)s][%(levelname)s](%(filename)s:%(lineno)s) %(message)s')
    file_handler.setFormatter(file_formatter)

    return file_handler


def _bot_logger():
    logger = logging.getLogger('Bot')
    logger.setLevel(logging.INFO)

    console_handler = _bot_console_handler()
    file_handler = _bot_file_handler()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def _trade_logger():
    logger = logging.getLogger('Trade')
    logger.setLevel(logging.INFO)

    console_handler = _bot_console_handler()
    console_handler.setFormatter(logging.Formatter('[%(name)s][%(strategyid)s][%(levelname)s] %(message)s'))
    current_dir = os.path.dirname(__file__)
    file = os.path.join(current_dir, 'logs/trades/bot_trade.log')
    file_handler = _bot_file_handler(file=file)
    ffmt = logging.Formatter('[%(asctime)s][%(strategyid)s][%(levelname)s](%(filename)s:%(lineno)s) %(message)s')
    file_handler.setFormatter(ffmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


bot_logger = _bot_logger()
trade_logger = _trade_logger()
bot_file_handler = _bot_file_handler()
bot_console_handler = _bot_console_handler()


def add_logging_directions(webhook_url=None, email={}):
    logger = logging.getLogger()

    if webhook_url is not None:
        slack_handler = SlackHandler(webhook_url)
        slack_handler.setFormatter(SlackFormatter('[%(asctime)s][%(levelname)s](%(filename)s:%(lineno)s) %(message)s'))
        logger.addHandler(slack_handler)

    if len(email) > 0:
        mail_handler = logging.handlers.SMTPHandler(mailhost=email['mailhost'],
                                                    fromaddr=email['fromaddr'],
                                                    toaddrs=email['toaddrs'],
                                                    subject=email['subject'])
        logger.addHandler(mail_handler)
