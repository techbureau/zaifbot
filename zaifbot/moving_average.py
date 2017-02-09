# moving_average.py

import sqlite3
import time
import urllib.request
import json
import sqlalchemy.pool as pool
from zaifapi import ZaifPublicApi
from db import Tradelogs, MovingAverage
import numpy as np

PERIOD_SECS = {'1d': 86400, '12h': 43200, '8h': 28800, '4h': 14400,
               '1h': 3600, '1m': 60, '5m': 300, '15m': 900, '30m': 1800}


def _check_tradelogs(currency_pair, period, length, start_time, end_time, count):
    _tradelogs = Tradelogs(currency_pair, period)

    # create tradelogs table if not exsit
    _tradelogs.create_table()

    # get tradelogs count
    _tradelogs_count = _tradelogs.get_tradelogs_count(end_time, start_time)

    # update tradelogs from API if some tradelogs are missing
    if _tradelogs_count < (count + length - 1):
        _public_api = ZaifPublicApi()
        _tradelogs_api_result = _public_api.everything('ohlc_data', currency_pair, {
            'period': period, 'count': count + length - 1, 'to_epoch_time': end_time})

        _tradelogs.update_tradelog(_tradelogs_api_result)


def _check_moving_average(currency_pair, period, length, start_time, end_time, count, sma_ema):
    _moving_average = MovingAverage(
        currency_pair, period, length, sma_ema)

    # create moving_average table if not exsit
    _moving_average.create_table()

    # get moving_average from table
    _mv_avrg_result = _moving_average.get_moving_average(end_time, start_time)

    _sma = []
    _ema = []
    _insert_params = []

    for i in range(0, len(_mv_avrg_result)):
        _nums = []
        _params = []

        if i > (length - 2) and _mv_avrg_result[i][3] is None:
            # prepare numbers to calculate moving average
            for j in range(0, length):
                _nums.append(_mv_avrg_result[i - j][1])

            if sma_ema == 'sma':
                # calculate sma
                _value = np.sum(_nums) / length
                _sma.append(
                    {'time_stamp': _mv_avrg_result[i][0], 'value': _value})

            if(_mv_avrg_result[i][2] == 1):
                _insert_params.append((_mv_avrg_result[i][0], _value))

        elif i > (length - 2):
            if sma_ema == 'sma':
                _sma.append({'time_stamp': _mv_avrg_result[i][
                    0], 'value': _mv_avrg_result[i][2]})
            elif sma_ema == 'ema':
                _ema.append({'time_stamp': _mv_avrg_result[i][
                    0], 'value': _mv_avrg_result[i][2]})

    _moving_average.update_moving_average(_insert_params)


def get_moving_average(currency_pair, count=1000, to_epoch_time=int(time.time()), period='1d', length=5, sma_ema='sma'):
    _LIMIT_COUNT = 1000
    _start_time = to_epoch_time - ((count + length) * PERIOD_SECS[period])
    _end_time = to_epoch_time

    count = min(count, _LIMIT_COUNT)

    _check_tradelogs(currency_pair, period, length,
                     _start_time, _end_time, count)

    _check_moving_average(currency_pair, period, length,
                          _start_time, _end_time, count, sma_ema)
