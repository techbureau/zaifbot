import time
from zaifbot.modules.moving_average import TradeLogs, MovingAverage
import numpy as np

PERIOD_SECS = {'1d': 86400, '12h': 43200, '8h': 28800, '4h': 14400,
               '1h': 3600, '1m': 60, '5m': 300, '15m': 900, '30m': 1800}
LIMIT_COUNT = 1000


def _check_trade_logs(currency_pair, period, length, start_time, end_time, count):
    tradelogs = TradeLogs(currency_pair, period)

    # create tradelogs table if not exsit
    tradelogs.create_table()
    '''
    # get tradelogs count
    tradelogs_count = tradelogs.get_tradelogs_count(end_time, start_time)

    # update tradelogs from API if some tradelogs are missing
    if tradelogs_count < (count + length - 1):
        public_api = ZaifPublicApi()
        trdlgs_api_rtrn = public_api.everything('ohlc_data', currency_pair,
                                                {'period': period,
                                                 'count': count + length - 1,
                                                 'to_epoch_time': end_time})

        tradelogs.create_data(trdlgs_api_rtrn)
    '''


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


def get_moving_average(currency_pair, count=LIMIT_COUNT,
                       to_epoch_time=int(time.time()), period='1d',
                       length=5, sma_ema='sma'):
    start_time = to_epoch_time - ((count + length) * PERIOD_SECS[period])

    count = min(count, LIMIT_COUNT)

    _check_trade_logs(currency_pair, period, length, start_time, to_epoch_time, count)

    # _check_moving_average(currency_pair, period, length,
    #                      start_time, to_epoch_time, count, sma_ema)


def _calculate_ema(current_val, last_val, length):
    k = 2 / (length + 1)
    ema = current_val * k + last_val * (1 - k)

    return ema
