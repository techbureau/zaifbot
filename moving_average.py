# moving_average.py

import sqlite3
import time
import urllib.request
import json
import sqlalchemy.pool as pool
from zaifapi import ZaifPublicApi

PERIOD_SECS = {'1d': 86400, '12h': 43200, '8h': 28800, '4h': 14400,
               '1h': 3600, '1m': 60, '5m': 300, '15m': 900, '30m': 1800}


def getconn():
    creator = sqlite3.connect('zaif_bot.db')
    return creator


def check_tradelogs(currency_pair, period, length, to_epoch_time, count):
    start_time = to_epoch_time - \
        ((count + length) * PERIOD_SECS[period])
    end_time = to_epoch_time
    table_name = 'tradelogs_' + currency_pair + '_' + period

    # create tradelog table if not exsit
    create_table = 'CREATE TABLE IF NOT EXISTS ' + table_name + \
        '(time INT PRIMARY KEY ASC, open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL, close REAL NOT NULL, average REAL NOT NULL, volume REAL NOT NULL, closed INT NOT NULL)'
    conn.execute(create_table)

    # get tradelogs
    query = 'SELECT COUNT(time) FROM ' + table_name + \
        ' WHERE time <= ? AND time > ? AND closed = 1;'
    params = (end_time, start_time)
    cursor.execute(query, params)
    trade_logs_count = cursor.fetchone()

    # update tradelogs from API if some tradelogs are missing
    if trade_logs_count[0] < (count + length):
        public_api = ZaifPublicApi()
        tradelogs = public_api.everything('ohlc_data', currency_pair, {'period': period, 'count': count})

        insert_params = []
        update_params = []
        for i in tradelogs:
            insert_params.append((i['time'], i['open'], i['high'], i['low'], i[
                                  'close'], i['average'], i['volume'], int(i['closed'])))
            update_params.append((i['open'], i['high'], i['low'], i['close'], i[
                                  'average'], i['volume'], int(i['closed']), i['time']))


        insert_query = 'INSERT OR IGNORE INTO ' + table_name + ' (time, open, high, low, close, average, volume, closed) VALUES(?,?,?,?,?,?,?,?);'
        update_query = 'UPDATE ' + table_name + ' SET open=?, high=?, low=?,close=?,average=?, volume=?,closed=? WHERE time=? AND closed=0;'
        conn.executemany(insert_query, insert_params)
        conn.executemany(update_query, update_params)

    conn.commit()


def get_sma(currency_pair, count=1000, to_epoch_time=int(time.time()), period="1d", length=5):
    global conn, cursor

    mypool = pool.QueuePool(getconn, max_overflow=10, pool_size=5)
    conn = mypool.connect()
    cursor = conn.cursor()

    check_tradelogs(currency_pair, period, length, to_epoch_time, count)

    query = 'SELECT * FROM tradelogs_' + currency_pair + '_' + period
    # print(query)
