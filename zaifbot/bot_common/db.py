import threading
from abc import ABCMeta
from sqlalchemy import create_engine


class _DbConnectionPool(metaclass=ABCMeta):
    _instance = None
    _lock = threading.Lock()
    _engine = None
    _test = 'test'

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._engine = cls.get_connection_instance()
        return cls._instance

    def get_con(self):
        engine = self._engine.connect()
        return engine

    @classmethod
    def get_connection_instance(cls):
        raise NotImplementedError()


class _Sqlite3Pool(_DbConnectionPool):
    _DB_NAME = 'zaif_bot.db'

    @classmethod
    def get_connection_instance(cls):
        return create_engine('sqlite:///{}'.format(cls._DB_NAME), echo='debug')


class DbAccessor(metaclass=ABCMeta):
    def __init__(self):
        # マルチDBを実装する際、ここをよしなに修正する
        self._engine = _Sqlite3Pool()

    def get_connection(self):
        return self._engine.get_con()
