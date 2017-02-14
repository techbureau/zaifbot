from sqlalchemy import and_
from zaifbot.modules.dao import DaoBase
from zaifbot.models.moving_avarage.moving_average import TradeLogs


class TradeLogsDao(DaoBase):
    _INSERT = """
        INSERT OR IGNORE
        INTO {}
        (
            time,
            open,
            high,
            low,
            close,
            average,
            volume,
            closed
        )
        VALUES
            (?,?,?,?,?,?,?,?)
    """

    _UPDATE = """
        UPDATE {}
        SET
            open=?,
            high=?,
            low=?,
            close=?,
            average=?,
            volume=?,
            closed=?
        WHERE
            time=?
            AND closed=0;

    """

    def __init__(self, currency_pair, period):
        super().__init__()
        self._currency_pair = currency_pair
        self._period = period
        self._table_name = 'trade_logs_{}_{}'.format(currency_pair, period)

    def get_model(self):
        return TradeLogs

    def get_record(self, end_time, start_time):
        session = self.get_session()
        return session.query(self.model).filter(and_(self.model.time <= end_time,
                                                     self.model.time >= start_time,
                                                     self.model.currency_pair == self._currency_pair,
                                                     self.model.period == self._period,
                                                     self.model.closed == 1)).all()

    def create_data(self, trade_logs, currency_pair, period):
        session = self.get_session()
        insert = self.model(time=trade_logs[100]['time'], currency_pair=currency_pair,
                     period=period, open=trade_logs[100]['open'],
                       high=trade_logs[100]['high'], low=trade_logs[100]['low'],
                       close=trade_logs[100]['close'], average=trade_logs[100]['average'],
                       volume=trade_logs[100]['volume'], closed=trade_logs[100]['closed'])

        session.add(insert)
        session.commit()
        '''
        insert_params = []
        update_params = []
        for i in trade_logs:
            insert_params.append((i['time'], i['open'], i['high'], i['low'],
                                  i['close'], i['average'], i['volume'],
                                  int(i['closed'])))
            update_params.append((i['open'], i['high'], i['low'], i['close'],
                                  i['average'], i['volume'], int(i['closed']),
                                  i['time']))

        # insert if missing or update if exist but not closed
        insert_query = self._INSERT.format(self._table_name)
        update_query = self._UPDATE.format(self._table_name)
        self._instance.conn.executemany(insert_query, insert_params)
        self._instance.conn.executemany(update_query, update_params)
        self._instance.conn.commit()
        '''
# class MovingAverage(DbAccessor):
#     _CREATE_TABLE = """
#       CREATE TABLE IF NOT EXISTS {}
#       (
#         time INT PRIMARY KEY ASC,
#         sma REAL,
#         ema REAL
#       )
#     """
#
#     _SELECT = """
#         SELECT
#             T1.time, T1.close, T1.closed, T2.{}
#         FROM
#             {} AS T1 LEFT JOIN {} AS T2 ON T1.time = T2.time
#         WHERE
#             T1.time < ?
#             AND T1.time > ?
#     """
#
#     _INSERT = """
#         INSERT OR IGNORE
#         INTO {}
#             (time, {})
#         VALUES
#             (?,?)
#     """
#
#     def __init__(self, currency_pair, period, length, sma_ema):
#         #self._instance = ZaifbotDb()
#         self._trdlg_table_name = 'tradelogs_{}_{}'.format(
#             currency_pair, period)
#         self._mvavrg_table_name = 'moving_average_{}_{}_{}'.format(
#             currency_pair, period, str(length))
#         self._sma_ema = sma_ema
#
#     def create_table(self):
#         self._instance.conn.execute(
#             self._CREATE_TABLE.format(self._mvavrg_table_name))
#
#     def get_moving_average(self, end_time, start_time):
#         query = self._SELECT.format(self._sma_ema, self._trdlg_table_name,
#                                     self._mvavrg_table_name)
#         params = (end_time, start_time)
#         self._instance.cursor.execute(query, params)
#         moving_average = self._instance.cursor.fetchall()
#
#         return moving_average
#
#     def update_moving_average(self, insert_params):
#         insert_query = self._INSERT.format(self._mvavrg_table_name,
#                                            self._sma_ema)
#         self._instance.conn.executemany(insert_query, insert_params)
#         self._instance.conn.commit()
