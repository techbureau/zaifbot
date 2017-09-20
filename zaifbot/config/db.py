import os
from sqlalchemy import create_engine
from .handler import ConfigFileHandler


def _default_database_path():
    parentdir = os.path.dirname(os.path.dirname(__file__))
    targetdir = os.path.join(parentdir, 'db')
    return 'sqlite:///{}'.format(os.path.join(targetdir, 'zaifbot.db'))


def _get_database_url():
    config = ConfigFileHandler()
    url_option = config.read_by_section_and_key('db', 'url')
    if url_option:
        return url_option

    return _default_database_path()


Engine = create_engine(_get_database_url())
