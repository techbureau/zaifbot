import os
import logging.handlers
from slack_logger import SlackHandler, SlackFormatter


def _bot_logger():
    logger = logging.getLogger('zaif_bot_logger')
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    # parent = os.path.dirname(os.path.dirname(__file__))
    current_dir = os.path.dirname(__file__)
    target_file = os.path.join(current_dir, 'logs/zaifbot.log')
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=target_file)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s][%(levelname)s](%(filename)s:%(lineno)s) %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def _trade_logger():
    logger = logging.getLogger('trade_logger')
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # parent = os.path.dirname(os.path.dirname(__file__))
    current_dir = os.path.dirname(__file__)
    target_file = os.path.join(current_dir, 'logs/trades/bot_trade.log')
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=target_file)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


bot_logger = _bot_logger()
trade_logger = _trade_logger()


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
