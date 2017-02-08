# moving_average.py

import sqlite3
import time
import urllib.request
import json
import sqlalchemy.pool as pool
from zaifapi import ZaifPublicApi
from db import Tradelogs, MovingAverage

PERIOD_SECS = {'1d': 86400, '12h': 43200, '8h': 28800, '4h': 14400,
               '1h': 3600, '1m': 60, '5m': 300, '15m': 900, '30m': 1800}
DB_NAME = 'zaif_bot.db'
DB_KIND = 'sqlite3'


def check_tradelogs(currency_pair, period, length, start_time, end_time, count):
    tradelogs = Tradelogs(DB_KIND, DB_NAME, currency_pair, period)
    
    # create tradelogs table if not exsit
    tradelogs.create_table()

    # get tradelogs count
    tradelogs_count = tradelogs.get_tradelogs_count(end_time, start_time)

    # update tradelogs from API if some tradelogs are missing
    if tradelogs_count < (count + length - 1):
        public_api = ZaifPublicApi()
        tradelogs_api = public_api.everything('ohlc_data', currency_pair, {'period': period, 'count': count + length - 1, 'to_epoch_time': end_time})

        tradelogs.update_tradelog(tradelogs_api)

def check_moving_average(currency_pair, period, length, start_time, end_time, count, sma_ema):
    moving_average = MovingAverage(DB_KIND, DB_NAME, currency_pair, period, length, sma_ema)

    # create moving_average table if not exsit
    moving_average.create_table()

    # get moving_average from table
    mv_avrg_result = moving_average.get_moving_average(end_time, start_time)
    
    sma = []
    ema = []
    insert_params = []

    for i in range(0, len(mv_avrg_result)):
        nums = []
        params = []

        if i > (length - 2) and mv_avrg_result[i][3] is None:
            # prepare numbers to calculate moving average
            for j in range(0, length):
                nums.append(mv_avrg_result[i-j][1])

            if sma_ema == 'sma':
                value = calculate_sma(nums, length)
                sma.append({'time_stamp': mv_avrg_result[i][0],'value': value})

            if(mv_avrg_result[i][2] == 1):
                insert_params.append((mv_avrg_result[i][0], value))
                
        elif i > (length - 2):
            if sma_ema == 'sma':
                sma.append({'time_stamp': mv_avrg_result[i][0],'value': mv_avrg_result[i][2]})
            elif sma_ema == 'ema':
                ema.append({'time_stamp': mv_avrg_result[i][0],'value': mv_avrg_result[i][2]})

    moving_average.update_moving_average(insert_params)

def get_moving_average(currency_pair, count=1000, to_epoch_time=int(time.time()), period="1d", length=5, sma_ema='sma'):
    start_time = to_epoch_time - ((count + length) * PERIOD_SECS[period])
    end_time = to_epoch_time

    if(count > 1000):
        count = 1000

    check_tradelogs(currency_pair, period, length, start_time, end_time, count)

    check_moving_average(currency_pair, period, length, start_time, end_time, count, sma_ema)

def calculate_sma(nums, length):
    sum = 0

    for i in nums:
        sum = sum + i

    result = sum / length

    return result
