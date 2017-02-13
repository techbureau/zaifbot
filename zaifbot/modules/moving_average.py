from bot_common.db import ZaifbotDb

class Tradelogs():
    _CREATE_TABLE = """
      CREATE TABLE IF NOT EXISTS {}
      (
        time INT PRIMARY KEY ASC,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        average REAL NOT NULL,
        volume REAL NOT NULL,
        closed INT NOT NULL
      )
    """

    def __init__(self, currency_pair, period):
        self._instance = ZaifbotDb()
        self._table_name = 'tradelogs_{}_{}'.format(currency_pair, period)

    def create_table(self):
        self._instance.conn.execute(
            self._CREATE_TABLE.format(self._table_name))

    def get_tradelogs_count(self, end_time, start_time):
        query = 'SELECT COUNT(time) FROM {} WHERE time < ? AND time > ? AND closed = 1;'.format(
            self._table_name)
        params = (end_time, start_time)
        self._instance.cursor.execute(query, params)
        trade_logs_count = self._instance.cursor.fetchone()

        return trade_logs_count[0]

    def update_tradelog(self, tradelogs_api):
        insert_params = []
        update_params = []
        for i in tradelogs_api:
            insert_params.append((i['time'], i['open'], i['high'], i['low'], i[
                                 'close'], i['average'], i['volume'], int(i['closed'])))
            update_params.append((i['open'], i['high'], i['low'], i['close'], i[
                                 'average'], i['volume'], int(i['closed']), i['time']))

        # insert if missing
        insert_query = 'INSERT OR IGNORE INTO {} (time, open, high, low, close, average, volume, closed) VALUES(?,?,?,?,?,?,?,?);'.format(
            self._table_name)
        self._instance.conn.executemany(insert_query, insert_params)
        self._instance.conn.commit()


class MovingAverage():
    _CREATE_TABLE = """
      CREATE TABLE IF NOT EXISTS {}
      (
        time INT PRIMARY KEY ASC,
        sma REAL,
        ema REAL
      )
    """

    def __init__(self, currency_pair, period, length, sma_ema):
        self._instance = ZaifbotDb()
        self._trdlg_table_name = 'tradelogs_{}_{}'.format(
            currency_pair, period)
        self._mvavrg_table_name = 'moving_average_{}_{}_{}'.format(
            currency_pair, period, str(length))
        self._sma_ema = sma_ema

    def create_table(self):
        self._instance.conn.execute(
            self._CREATE_TABLE.format(self._mvavrg_table_name))

    def get_moving_average(self, end_time, start_time):
        query = 'SELECT T1.time, T1.close, T1.closed, T2.{} FROM {} AS T1 LEFT JOIN {} AS T2 ON T1.time = T2.time WHERE T1.time < ? AND T1.time > ?;'.format(
            self._sma_ema, self._trdlg_table_name, self._mvavrg_table_name)
        params = (end_time, start_time)
        self._instance.cursor.execute(query, params)
        moving_average = self._instance.cursor.fetchall()

        return moving_average

    def update_moving_average(self, insert_params):
        insert_query = 'INSERT OR IGNORE INTO {} (time, {}) VALUES(?,?);'.format(
            self._mvavrg_table_name, self._sma_ema)
        self._instance.conn.executemany(insert_query, insert_params)
        self._instance.conn.commit()