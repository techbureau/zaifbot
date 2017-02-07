# moving_average.py
import sqlite3
import time
import urllib.request
import json

conn = sqlite3.connect('zaif.db')
cursor = conn.cursor()
period_secs = {'1d': 86400, '12h': 43200, '8h': 28800, '4h': 14400,
               '1h': 3600, '1m': 60, '5m': 300, '15m': 900, '30m': 1800}


def check_tradelogs(currency_pair, period, length, to_epoch_time, count):
    global conn, boolean, cursor

    start_time = to_epoch_time - ((count + length) * period_secs[period])
    end_time = to_epoch_time
    table_name = 'tradelogs_' + currency_pair + '_' + period

    # create tradelog table if not exsit
    query = 'CREATE TABLE IF NOT EXISTS ' + table_name + \
        '(time INT PRIMARY KEY ASC, open REAL NOT NULL,high REAL NOT NULL, low REAL NOT NULL,close REAL NOT NULL,average REAL NOT NULL,volume REAL NOT NULL,closed INT NOT NULL)'
    conn.execute(query)

    # get tradelogs
    query = "SELECT COUNT(time) FROM {0:s} WHERE time >= {1:d} AND time > {2:d} AND closed = 1;".format(
        table_name, end_time, start_time)
    cursor.execute(query)
    trade_logs_count = cursor.fetchone()

    # update tradelogs from API if some tradelogs are missing
    if trade_logs_count[0] < (count + length):
        jdec = json.JSONDecoder()
        url = "https://api.zaif.jp/api/1/ohlc_data/{0:s}?period={1:s}&to_epoch_time={2:d}&count={3:d}".format(
            currency_pair, period, to_epoch_time, count)
        response = urllib.request.urlopen(url)
        tradelogs = jdec.decode(response.read().decode('utf-8'))

        for i in tradelogs:
            query = "INSERT OR IGNORE INTO {0:s} (time, open, high, low, close, average, volume, closed) VALUES({1:d},{2:f},{3:f},{4:f},{5:f},{6:f},{7:f},{8:d});".format(
                table_name, i['time'], i['open'], i['high'], i['low'], i['close'], i['average'], i['volume'], int(i['closed']))
            conn.execute(query)
            query = "UPDATE {0:s} SET open={1:f}, high={2:f}, low={3:f},close={4:f},average={5:f}, volume={6:f},closed={7:d} WHERE time={8:d} AND closed=0;".format(
                table_name, i['open'], i['high'], i['low'], i['close'], i['average'], i['volume'], int(i['closed']), i['time'])
            conn.execute(query)

    conn.commit()


def get_sma(currency_pair, count=1000, to_epoch_time=int(time.time()), period="1d", length=5):
    check_tradelogs(currency_pair, period, length, to_epoch_time, count)

    query = 'SELECT * FROM tradelogs_' + currency_pair + '_' + period
    print(query)