import os
from sqlalchemy import create_engine
from .file import ConfigFileHandler
from sqlalchemy.engine.url import URL as EngineURL


def _default_database_path():
    parentdir = os.path.dirname(os.path.dirname(__file__))
    targetdir = os.path.join(parentdir, 'db')
    return 'sqlite:///{}'.format(os.path.join(targetdir, 'zaifbot.db'))


def get_database_url(config=None):
    config = config or ConfigFileHandler()
    engine_option = config.read_by_section('db')
    if engine_option is None:
        return _default_database_path()
    return EngineURL(**engine_option)


Engine = create_engine(get_database_url())
