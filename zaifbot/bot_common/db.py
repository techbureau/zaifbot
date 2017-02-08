import sqlalchemy.pool as pool
import sqlite3
from zaifapi import ZaifPublicApi


class ZaifbotDb:

    def __init__(self, db_kind, db_name):
        self.db_name = db_name
        self.db_kind = db_kind

        self.connect_db()

    def connect_db(self):
        self.pool = pool.QueuePool(self.getconn, max_overflow=10, pool_size=5)
        self.conn = self.pool.connect()
        self.cursor = self.conn.cursor()

    def getconn(self):
        if self.db_kind == 'sqlite3':
            c = sqlite3.connect(self.db_name)

            return c


class Tradelogs(ZaifbotDb):

    def __init__(self, db_kind, db_name, currency_pair, period):
        ZaifbotDb.__init__(self, db_kind, db_name)
        self.table_name = 'tradelogs_' + currency_pair + '_' + period

    def create_table(self):
        create_table = 'CREATE TABLE IF NOT EXISTS ' + self.table_name + \
            '(time INT PRIMARY KEY ASC, open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL, close REAL NOT NULL, average REAL NOT NULL, volume REAL NOT NULL, closed INT NOT NULL)'
        self.conn.execute(create_table)

    def get_tradelogs_count(self, end_time, start_time):
      query = 'SELECT COUNT(time) FROM ' + self.table_name + ' WHERE time < ? AND time > ? AND closed = 1;'
      params = (end_time, start_time)
      self.cursor.execute(query, params)
      trade_logs_count = self.cursor.fetchone()

      return trade_logs_count[0]

    def update_tradelog(self, tradelogs_api):
      insert_params = []
      update_params = []
      for i in tradelogs_api:
        insert_params.append((i['time'], i['open'], i['high'], i['low'], i['close'], i['average'], i['volume'], int(i['closed'])))
        update_params.append((i['open'], i['high'], i['low'], i['close'], i['average'], i['volume'], int(i['closed']), i['time']))

      # insert if missing or update if exist but closed is 0
      insert_query = 'INSERT OR IGNORE INTO ' + self.table_name + ' (time, open, high, low, close, average, volume, closed) VALUES(?,?,?,?,?,?,?,?);'
      #update_query = 'UPDATE ' + self.table_name + ' SET open=?, high=?, low=?,close=?,average=?, volume=?,closed=? WHERE time=? AND closed=0;'
      self.conn.executemany(insert_query, insert_params)
      #self.conn.executemany(update_query, update_params)
      self.conn.commit()


class MovingAverage(ZaifbotDb):

    def __init__(self, db_kind, db_name, currency_pair, period, length, sma_ema):
        ZaifbotDb.__init__(self, db_kind, db_name)
        self.trdlg_table_name = 'tradelogs_' + currency_pair + '_' + period
        self.mvavrg_table_name = 'moving_average_' + currency_pair + '_' + period + '_' + str(length)
        self.sma_ema = sma_ema

    def create_table(self):
        create_table = 'CREATE TABLE IF NOT EXISTS ' + self.mvavrg_table_name + \
            '(time INT PRIMARY KEY ASC, sma REAL, ema REAL)'
        self.conn.execute(create_table)

    def get_moving_average(self, end_time, start_time):
      query = 'SELECT T1.time, T1.close, T1.closed, T2.' + self.sma_ema + ' FROM ' + self.trdlg_table_name + ' AS T1 LEFT JOIN '+ self.mvavrg_table_name +' AS T2 ON T1.time = T2.time WHERE T1.time < ? AND T1.time > ?;'
      params = (end_time, start_time)
      self.cursor.execute(query, params)
      moving_average = self.cursor.fetchall()
      
      return moving_average

    def update_moving_average(self, insert_params):
      insert_query = 'INSERT OR IGNORE INTO ' + self.mvavrg_table_name + ' (time, '+ self.sma_ema +') VALUES(?,?);'
      self.conn.executemany(insert_query, insert_params)
      self.conn.commit()
