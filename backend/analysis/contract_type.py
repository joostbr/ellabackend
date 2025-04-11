from datetime import datetime, timedelta
from backend.services.edw import DataPoint, TimeSeries, EDWApi
from backend.database.MySQLDatabase import MySQLDatabase
from backend.core.statistics import Statistics, StatisticsRepository
import pandas as pd
import pytz


class ContractTypeEvaluation:
    """
    Class to evaluate the contract type based on the provided data.
    """

    def __init__(self, fromdt, todt):
        self.fromdt = fromdt
        self.todt = todt
        self.edw_api = EDWApi()
        self.price_offtake_scaler = 1.0
        self.price_offtake_adder = 0.0
        self.price_injection_scaler = 1.0
        self.price_injection_adder = 0.0
        self.database = MySQLDatabase.instance()
        self.statistics_repo = StatisticsRepository()

    def _get_epex_data(self, fromdt, todt):
        """
        Fetch EPEX data from the database.
        """
        # Placeholder for database query
        # This should be replaced with actual database query logic
        return pd.DataFrame()

    def _get_endex_data(self, fromdt, todt, endex='101'):
        """
        Fetch ENDEX data from the database.
        """
        # Placeholder for database query
        # This should be replaced with actual database query logic
        return pd.DataFrame()

    def _get_timeseries_for_vault(self, vault_name: str):
        timeseries = self.edw_api.get_timeseries()
        all_ts = next(filter(lambda x: x.vaultName == vault_name, timeseries), None)
        return all_ts

    def _get_vault_digital_meter(self):
        vaults = self.edw_api.get_vaults()
        vault = next(filter(lambda x: x.name == "digital_meter", vaults), None)
        return vault

    def _get_avg_epex_sql(self, epex):
        from_utc = int(self.fromdt.astimezone(pytz.utc).timestamp()/60)
        to_utc = int(self.todt.astimezone(pytz.utc).timestamp()/60)
        sql = f"""(SELECT
                    t.utcstart,
                  t.localstart,
                  p.year,
                  p.month,
                  p.avg_monthly_price as price
                FROM edw.ts_times t
                LEFT JOIN (
                  SELECT
                    MIN(utcstart) as utcmonth,
                    YEAR(localstart) AS year,
                    MONTH(localstart) AS month,
                    AVG(price) AS avg_monthly_price
                  FROM edw.ts_prices
                  WHERE tsid = {epex.id} 
                  GROUP BY YEAR(localstart), MONTH(localstart)
                ) p
                  ON t.startmonth = p.utcmonth
                WHERE t.utcstart>={from_utc} and t.utcstart < {to_utc}
                ) p """
        return sql, None

    def _get_epex_sql(self, epex_ts):
        sql = f"""ts_prices p"""
        return sql,f" and  p.tsid = {epex_ts.id}"

    def _get_endex101_sql(self, endex_ts):
        sql = f"""ts_prices p"""
        return sql,f" and  p.tsid = {endex_ts.id}"


    def _get_endex103_sql(self, endex_ts):
        sql = f"""ts_prices p"""
        return sql,f" and  p.tsid = {endex_ts.id}"


    def _build_digital_meter_sql(self, ts, price_sql, join_sql):
        sql = (f"""select from_unixtime(m.utcstart * 60) as UTCTIME,m.localstart as TIME, (({self.price_scaler}*p.price+{self.price_adder})/1000)*m.offtake as OFFTAKE_COST, (({self.price_scaler}*p.price - {self.price_adder})/1000)*m.injection as INJECTION_PROFIT from 
                      ts_digital_meter m join {price_sql}
                      on m.utcstart = p.utcstart {join_sql if join_sql else ''}
                      where m.tsid = {ts.id} and m.utcstart >= {int(self.fromdt.timestamp() / 60)} and m.utcstart < {int(self.todt.timestamp() / 60)}
                      order by m.utcstart""")
        return sql

    def evaluate_digital_meter(self, ts, endex101, endex103, epex):

        epex_sql, join_epex_sql = self._get_epex_sql(epex)
        avg_epex_sql, join_avg_epex_sql = self._get_avg_epex_sql(epex)
        endex101_sql, join_endex101_sql = self._get_endex101_sql(endex101)
        endex103_sql, join_endex103_sql = self._get_endex103_sql(endex103)

        df_epex = self.database.query(sql=self._build_digital_meter_sql(ts, epex_sql, join_epex_sql), timecols=['utcstart'])
        df_avg_epex = self.database.query(sql=self._build_digital_meter_sql(ts, avg_epex_sql, join_avg_epex_sql), timecols=['utcstart'])
        df_endex101 = self.database.query(sql=self._build_digital_meter_sql(ts, endex101_sql, join_endex101_sql), timecols=['utcstart'])
        df_endex103 = self.database.query(sql=self._build_digital_meter_sql(ts, endex103_sql, join_endex103_sql), timecols=['utcstart'])

        now = datetime.utcnow()
        stats_to_insert = [
            Statistics(
                siteid='00000',
                tsid=ts.id,
                statkey='offtake/cost/epex',
                value=df_epex['OFFTAKE_COST'].sum(),
                description='Offtake cost according to EPEX',
                calculationtime=now,
                fromutc=self.fromdt,
                toutc=self.todt,
            ),
            Statistics(
                siteid='00000',
                tsid=ts.id,
                statkey='offtake/cost/average_epex',
                value=df_avg_epex['OFFTAKE_COST'].sum(),
                description='Offtake cost according to EPEX average',
                calculationtime=now,
                fromutc=self.fromdt,
                toutc=self.todt,
            ),
            Statistics(
                siteid='00000',
                tsid=ts.id,
                statkey='offtake/cost/endex101',
                value=df_endex101['OFFTAKE_COST'].sum(),
                description='Offtake cost according to ENDEX 101',
                calculationtime=now,
                fromutc=self.fromdt,
                toutc=self.todt,

            ),
            Statistics(
                siteid='00000',
                tsid=ts.id,
                statkey='offtake/cost/endex103',
                value=df_endex103['OFFTAKE_COST'].sum(),
                description='Offtake cost according to ENDEX 103',
                calculationtime=now,
                fromutc=self.fromdt,
                toutc=self.todt
            ),
            # Injection profit stats
            Statistics(
                siteid='00000',
                tsid=ts.id,
                statkey='injection/profit/epex',
                value=df_epex['INJECTION_PROFIT'].sum(),
                description='Injection profit according to EPEX',
                calculationtime=now,
                fromutc=self.fromdt,
                toutc=self.todt,
            ),
            Statistics(
                siteid='00000',
                tsid=ts.id,
                statkey='injection/profit/average_epex',
                value=df_avg_epex['INJECTION_PROFIT'].sum(),
                description='Injection profit according to EPEX average',
                calculationtime=now,
                fromutc=self.fromdt,
                toutc=self.todt,
            ),
            Statistics(
                siteid='00000',
                tsid=ts.id,
                statkey='injection/profit/endex101',
                value=df_endex101['INJECTION_PROFIT'].sum(),
                description='Injection profit according to ENDEX 101',
                calculationtime=now,
                fromutc=self.fromdt,
                toutc=self.todt,
            ),
            Statistics(
                siteid='00000',
                tsid=ts.id,
                statkey='injection/profit/endex103',
                value=df_endex103['INJECTION_PROFIT'].sum(),
                description='Injection profit according to ENDEX 103',
                calculationtime=now,
                fromutc=self.fromdt,
                toutc=self.todt,
            )
        ]

        # Bulk upsert them to the DB
        self.statistics_repo.bulk_upsert([s.__dict__ for s in stats_to_insert])




    def evaluate(self):
        from_utc = int(self.fromdt.astimezone(pytz.utc).timestamp()/60)
        to_utc = int(self.todt.astimezone(pytz.utc).timestamp()/60)

        all_ts = self.edw_api.get_timeseries()

        endex101 = next(filter(lambda x: x.name == "endex/101/15", all_ts), None)
        endex103 = next(filter(lambda x: x.name == "endex/103/15", all_ts), None)
        epex15 = next(filter(lambda x: x.name == "Epex/BE/15", all_ts), None)

        ean_ts = list(filter(lambda x: x.vaultName == "digital_meter", all_ts))
        for each in ean_ts:
            print(ean_ts)
            self.evaluate_digital_meter(ts=each, endex101=endex101, endex103=endex103, epex=epex15)





ContractTypeEvaluation(datetime.now(pytz.UTC)-timedelta(days=365), datetime.now(pytz.UTC)).evaluate()