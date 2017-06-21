import logging
import os
from slack_logger import SlackHandler, SlackFormatter


def save_trade_log(logger, filename, webhook_url=None, email={}):
    dir_path = os.path.abspath(os.path.dirname(__file__))
    log_path = os.path.join(dir_path, filename)
    logging.config.fileConfig(os.path.join(dir_path, 'logging.conf'),
                              defaults={'log_path': repr(log_path)})
    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    logger.addHandler(console_handler)

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
    return logger
