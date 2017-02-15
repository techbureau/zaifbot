import time
import numpy as np
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT
from zaifbot.modules.moving_average import TradeLogsManager


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

            if (mv_avrg_result[i][2] == 1):
                insert_params.append((mv_avrg_result[i][0], value))

        elif i > (length - 2):
            if sma_ema == 'sma':
                sma.append({'time_stamp': mv_avrg_result[i][
                    0], 'value': mv_avrg_result[i][2]})
            elif sma_ema == 'ema':
                ema.append({'time_stamp': mv_avrg_result[i][
                    0], 'value': mv_avrg_result[i][2]})

    moving_average.update_moving_average(insert_params)


def get_moving_average(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
                       to_epoch_time=int(time.time()),
                       length=5, sma_ema='sma'):
    count = min(count, LIMIT_COUNT)
    end_time = to_epoch_time - (to_epoch_time % PERIOD_SECS[period])
    start_time = end_time - ((count + length) * PERIOD_SECS[period])
    trade_logs = TradeLogsManager(currency_pair, period)
    trade_logs.setup(start_time, end_time)

    # _check_moving_average(currency_pair, period, length,
    #                      start_time, to_epoch_time, count, sma_ema)


def _calculate_ema(current_val, last_val, length):
    k = 2 / (length + 1)
    ema = current_val * k + last_val * (1 - k)

    return ema
