import os
import logging.config
dir_path = os.path.abspath(os.path.dirname(__file__))
log_path = os.path.join(dir_path, 'zaifbot.log')
logging.config.fileConfig(os.path.join(dir_path, 'logging.conf'),
                          defaults={'log_path': repr(log_path)})

logger = logging.getLogger()
