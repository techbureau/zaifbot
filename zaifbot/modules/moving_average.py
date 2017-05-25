import numpy as np
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT
from zaifbot.bot_common.logger import logger
from zaifbot.models.moving_average import TradeLogs, MovingAverages
from zaifbot.modules.api.wrapper import BotPublicApi
from zaifbot.modules.dao.moving_average import TradeLogsDao, MovingAverageDao
import pandas as pd


def get_need_epoch_times(start_time, end_time, period):
    while True:
        yield start_time
        start_time += PERIOD_SECS[period]
        if start_time >= end_time:
            yield end_time
            break


class TradeLogsSetUp:
    def __init__(self, currency_pair, period, count, length):
        self._currency_pair = currency_pair
        self._period = period
        self._count = count
        self._length = length
        self._trade_logs = TradeLogsDao(self._currency_pair, self._period)

    def execute(self, start_time, end_time):
        target_epoch_times = pd.DataFrame(index=self._get_target_epoch_times(start_time, end_time))
        if len(target_epoch_times.index) == 0:
            return True
        api_records = pd.DataFrame(self._get_ohlc_data_from_server(end_time))

        if api_records.empty:
            return False
        target_trade_logs_record = api_records.join(target_epoch_times, on='time', how='inner')
        target_trade_logs_record['currency_pair'] = self._currency_pair
        target_trade_logs_record['period'] = self._period
        return self._trade_logs.create_data(target_trade_logs_record)

    def _get_target_epoch_times(self, start_time, end_time):
        trade_logs_record = self._trade_logs.get_records(end_time, start_time, True)
        return self._check_missing_records(trade_logs_record, start_time, end_time, self._period)

    @staticmethod
    def _check_missing_records(trade_logs_record, start_time, end_time, period):
        to_epoch_times = set([x.time for x in trade_logs_record])
        target_epoch_times = set()
        for need_epoch_time in get_need_epoch_times(start_time, end_time, period):
            if need_epoch_time not in to_epoch_times:
                target_epoch_times.add(need_epoch_time)
        return target_epoch_times

    def _set_trade_logs_model_data(self, target_trade_logs_record):
        trade_logs_model_data = []
        for trade_logs in target_trade_logs_record:
            trade_logs_model_data.append(TradeLogs(
                time=trade_logs['time'],
                currency_pair=self._currency_pair,
                period=self._period,
                open=trade_logs['open'],
                high=trade_logs['high'],
                low=trade_logs['low'],
                close=trade_logs['close'],
                average=trade_logs['average'],
                volume=trade_logs['volume'],
                closed=int(trade_logs['closed'])
            ))
        return trade_logs_model_data

    def _get_ohlc_data_from_server(self, end_time):
        public_api = BotPublicApi()
        api_params = {'period': self._period, 'count': LIMIT_COUNT, 'to_epoch_time': end_time + 1}
        try:
            api_record = public_api.everything('ohlc_data', self._currency_pair, api_params)
        except Exception as e:
            logger.error(e)
            api_record = []
        required_count = self._count + self._length
        if required_count <= LIMIT_COUNT:
            return api_record
        count = required_count - LIMIT_COUNT
        second_end_time = end_time - (LIMIT_COUNT * PERIOD_SECS[self._period]) + 1
        second_api_params =\
            {'period': self._period, 'count': count, 'to_epoch_time': second_end_time}
        try:
            second_api_record =\
                public_api.everything('ohlc_data', self._currency_pair, second_api_params)
        except Exception as e:
            logger.error(e)
            second_api_record = []
        api_record = second_api_record + api_record
        return api_record


class MovingAverageSetUp:
    def __init__(self, currency_pair, period, count, length):
        self._currency_pair = currency_pair
        self._period = period
        self._count = count
        self._length = length
        self._moving_average = MovingAverageDao(self._currency_pair, self._period, self._length)

    def execute(self, ma_start_time, tl_start_time, end_time):
        moving_average_model_data = set()
        target_epoch_times = self._get_target_epoch_times(ma_start_time, end_time)
        if len(target_epoch_times) == 0:
            return True
        trade_logs_moving_average =\
            self._moving_average.get_trade_logs_moving_average(end_time, tl_start_time)
        for i in self._get_moving_average(trade_logs_moving_average, target_epoch_times):
            moving_average_model_data.add(self._get_moving_average_model_dataset(i['time'],
                                                                                 i['sma'],
                                                                                 i['ema'],
                                                                                 i['closed']))
        return self._moving_average.create_data(moving_average_model_data)

    def _get_target_epoch_times(self, start_time, end_time):
        moving_average_record = self._moving_average.get_records(end_time, start_time, True)
        return self._check_missing_records(moving_average_record,
                                           start_time,
                                           end_time,
                                           self._period)

    @staticmethod
    def _check_missing_records(moving_average_record, start_time, end_time, period):
        to_epoch_times = set([x.time for x in moving_average_record])
        target_epoch_times = set()
        for need_epoch_time in get_need_epoch_times(start_time, end_time, period):
            if need_epoch_time not in to_epoch_times:
                target_epoch_times.add(need_epoch_time)
        return target_epoch_times

    def _get_moving_average(self, trade_logs_moving_average, target_epoch_times):
        moving_average = {'time': 0}
        for i in range(self._length, len(trade_logs_moving_average)):
            if trade_logs_moving_average[i].TradeLogs.time in target_epoch_times:
                nums = self._get_nums(trade_logs_moving_average, i)
                sma = self._get_sma(nums)
                ema = self._get_ema(trade_logs_moving_average[i - 1], nums, moving_average)
                moving_average = {'time': trade_logs_moving_average[i].TradeLogs.time,
                                  'sma': sma,
                                  'ema': ema,
                                  'closed': trade_logs_moving_average[i].TradeLogs.closed}
                yield moving_average

    def _get_nums(self, trade_logs_moving_average, i):
        nums = []
        for j in range(0, self._length + 1):
            nums.append(trade_logs_moving_average[i - j].TradeLogs.close)
        return nums

    def _get_ema(self, last_trade_logs_moving_average, nums, moving_average):
        current_price = nums.pop(0)
        if last_trade_logs_moving_average.MovingAverages is not None\
                and last_trade_logs_moving_average.MovingAverages.closed:
            last_ema = last_trade_logs_moving_average.MovingAverages.ema
        elif last_trade_logs_moving_average.TradeLogs.time == moving_average['time']:
            last_ema = moving_average['ema']
        else:
            last_ema = np.average(nums)
        k = 2 / (self._length + 1)
        return current_price * k + last_ema * (1 - k)

    @staticmethod
    def _get_sma(nums):
        return np.average(nums[0:-1])

    def _get_moving_average_model_dataset(self, time, sma, ema, closed):
        return MovingAverages(
            time=time,
            currency_pair=self._currency_pair,
            period=self._period,
            length=self._length,
            sma=sma,
            ema=ema,
            closed=closed)
