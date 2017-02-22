import os
import logging.config
dir_path = os.path.abspath(os.path.dirname(__file__))
logging.config.fileConfig(os.path.join(dir_path, 'logging.conf'))


logger = logging.getLogger()
