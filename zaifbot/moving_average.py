import time
import numpy as np
from zaifbot.modules.dao.moving_average import TradeLogsDao
from zaifapi import ZaifPublicApi

PERIOD_SECS = {'1d': 86400, '12h': 43200, '8h': 28800, '4h': 14400,
               '1h': 3600, '1m': 60, '5m': 300, '15m': 900, '30m': 1800}
LIMIT_COUNT = 1000


def _check_trade_logs(currency_pair, period, length, start_time, end_time, count):
    tradelogs = TradeLogsDao(currency_pair, period)
    tradelogs_record = tradelogs.get_record(end_time, start_time)

    missing_records = _check_missing_records(tradelogs_record, start_time, end_time, count, period)

    if len(missing_records) > 0:
        api_records = _get_api_records(missing_records, currency_pair, period)
        for i in api_records:
            print(i)
        tradelogs.create_data(api_records, currency_pair, period)


def _check_missing_records(tradelogs_record, start_time, end_time, count, period):
    missing_records = []
    last_time = start_time

    for record in tradelogs_record:
        if record.time > (last_time + PERIOD_SECS[period]):
            to_epoch_time = (record.time - PERIOD_SECS[period])
            count = int((record.time - last_time) / PERIOD_SECS[period])
            missing_records.append({'to_epoch_time': to_epoch_time, 'count': count})

        last_time = record.time

    if last_time < (end_time - PERIOD_SECS[period]):
        count = int((end_time - last_time) / PERIOD_SECS[period])
        missing_records.append({'to_epoch_time': end_time, 'count': count})


    return missing_records


def _get_api_records(missing_records, currency_pair, period):
    api_records = []
    public_api = ZaifPublicApi()

    for record in missing_records:
        api_params = {'period': period, 'count': record['count'],
                      'to_epoch_time': record['to_epoch_time']}

        for each_record in public_api.everything('ohlc_data', currency_pair, api_params):
            api_records.append(each_record)

    return api_records


def _check_moving_average(currency_pair, period, length,
                          start_time, end_time, count, sma_ema):
    moving_average = MovingAverage(currency_pair, period, length, sma_ema)

    # create moving_average table if not exsit
    moving_average.create_table()

    # get moving_average from table
    mv_avrg_result = moving_average.get_moving_average(end_time, start_time)

    sma = []
    ema = []
    insert_params = []

    for i in range(0, len(mv_avrg_result)):
        nums = []

        if i > (length - 2) and mv_avrg_result[i][3] is None:
            if sma_ema == 'sma':
                # prepare numbers to calculate sma
                for j in range(0, length):
                    nums.append(mv_avrg_result[i - j][1])

                # calculate sma
                value = np.sum(nums) / length
                sma.append(
                    {'time_stamp': mv_avrg_result[i][0], 'value': value})
            elif sma_ema == 'ema':
                # for the first time ema calculation
                if len(ema) == 0:
                    # prepare numbers for first calculation of last value
                    for j in range(1, length + 1):
                        nums.append(mv_avrg_result[i - j][1])
                        print(nums)
                    last_val = np.sum(nums) / length
                else:
                    last_val = ema[i - 1]['value']

                # calculate ema
                value = _calculate_ema(
                    mv_avrg_result[i][1], last_val, length)
                ema.append(
                    {'time_stamp': mv_avrg_result[i][0], 'value': value})

            if(mv_avrg_result[i][2] == 1):
                insert_params.append((mv_avrg_result[i][0], value))

        elif i > (length - 2):
            if sma_ema == 'sma':
                sma.append({'time_stamp': mv_avrg_result[i][
                           0], 'value': mv_avrg_result[i][2]})
            elif sma_ema == 'ema':
                ema.append({'time_stamp': mv_avrg_result[i][
                           0], 'value': mv_avrg_result[i][2]})

    moving_average.update_moving_average(insert_params)


def get_moving_average(currency_pair, period='1d', count=LIMIT_COUNT,
                       to_epoch_time=int(time.time()),
                       length=5, sma_ema='sma'):
    count = min(count, LIMIT_COUNT)
    start_time = to_epoch_time - ((count + length) * PERIOD_SECS[period])

    _check_trade_logs(currency_pair, period, length, start_time, to_epoch_time, count)

    # _check_moving_average(currency_pair, period, length,
    #                      start_time, to_epoch_time, count, sma_ema)


def _calculate_ema(current_val, last_val, length):
    k = 2 / (length + 1)
    ema = current_val * k + last_val * (1 - k)

    return ema
