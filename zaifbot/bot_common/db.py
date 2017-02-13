import sqlalchemy.pool as pool
import sqlite3

DB_NAME = 'zaif_bot.db'


class ZaifbotDb:

    class __ZaifbotDb:

        def __init__(self):

            self.connect_db()

        def connect_db(self):
            self._pool = pool.QueuePool(
                self._getconn, max_overflow=10, pool_size=5)
            self.conn = self._pool.connect()
            self.cursor = self.conn.cursor()

        def _getconn(self):
            _c = sqlite3.connect(DB_NAME)

            return _c

    instance = None

    def __new__(class_):
        if not ZaifbotDb.instance:
            ZaifbotDb.instance = ZaifbotDb.__ZaifbotDb()

        return ZaifbotDb.instance
