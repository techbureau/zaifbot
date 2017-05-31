from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT
from zaifbot.bot_common.logger import logger
from zaifbot.models.moving_average import MovingAverages
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


def check_missing_records(exist_epoch_times, start_time, end_time, period):
    need_epoch_times = \
        set([x for x in get_need_epoch_times(start_time, end_time, period)])
    return need_epoch_times.difference(exist_epoch_times)


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
        trade_logs_record = \
            set(x.time for x in self._trade_logs.get_records(end_time, start_time, True))
        return check_missing_records(trade_logs_record, start_time, end_time, self._period)

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
        self._trade_logs = TradeLogsDao(self._currency_pair, self._period)

    def execute(self, ma_start_time, tl_start_time, end_time):
        moving_average_model_data = []
        target_epoch_times = \
            pd.DataFrame(index=self._get_target_epoch_times(ma_start_time, end_time))
        if len(target_epoch_times.index) == 0:
            return True
        trade_logs_moving_average =\
            self._get_trade_logs_moving_average(end_time, tl_start_time)
        for i in self._get_moving_average(trade_logs_moving_average, target_epoch_times):
            moving_average_model_data.append(self._get_moving_average_model_dataset(i['time'],
                                                                                    i['sma'],
                                                                                    i['ema'],
                                                                                    i['closed']))
        return self._moving_average.create_data(moving_average_model_data)

    def _get_target_epoch_times(self, start_time, end_time):
        moving_average_record = \
            set(x.time for x in self._moving_average.get_records(end_time, start_time, True))
        return \
            check_missing_records(moving_average_record, start_time, end_time, self._period)

    def _get_moving_average(self, trade_logs_moving_average, target_epoch_times):
        moving_average = {}
        for i in range(self._length, len(trade_logs_moving_average.index)):
            if trade_logs_moving_average.loc[i]['time'] in target_epoch_times.index:
                sma = trade_logs_moving_average.loc[i - self._length + 1:i]['close'].mean(axis=0)
                ema = self._get_ema(trade_logs_moving_average.loc[i - self._length:i])
                moving_average = {'time': int(trade_logs_moving_average.loc[i]['time']),
                                  'sma': sma, 'ema': ema,
                                  'closed': trade_logs_moving_average.loc[i]['closed']}
                yield moving_average

    def _get_trade_logs_moving_average(self, end_time, start_time):
        moving_average = \
            [i.__dict__ for i in self._moving_average.get_records(end_time, start_time, False)]
        trade_logs = \
            [j.__dict__ for j in self._trade_logs.get_records(end_time, start_time, False)]
        trade_logs_df = \
            pd.DataFrame(trade_logs, columns=['time', 'currency_pair', 'period', 'close', 'closed'])
        moving_average_df = \
            pd.DataFrame(moving_average, columns=['time', 'sma', 'ema', 'length'])
        trade_logs_moving_average = \
            trade_logs_df.merge(moving_average_df, left_on='time', right_on='time', how='outer')
        return trade_logs_moving_average

    def _get_ema(self, trade_logs_moving_average):
        k = 2 / (self._length + 1)
        if pd.isnull(trade_logs_moving_average.iloc[-2]['ema']):
            last_ema = trade_logs_moving_average.iloc[:-1]['close'].mean(axis=0)
        else:
            last_ema = trade_logs_moving_average.iloc[-2]['ema']
        return trade_logs_moving_average.iloc[-1]['close'] * k + last_ema * (1 - k)

    def _get_moving_average_model_dataset(self, time, sma, ema, closed):
        return MovingAverages(
            time=time,
            currency_pair=self._currency_pair,
            period=self._period,
            length=self._length,
            sma=sma,
            ema=ema,
            closed=closed)
