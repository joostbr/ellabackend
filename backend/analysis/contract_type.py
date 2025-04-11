from datetime import datetime, timedelta
from backend.services.edw import DataPoint, TimeSeries, EDWApi
from backend.database.MySQLDatabase import MySQLDatabase
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
        self.database = MySQLDatabase.instance()

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

    def _get_avg_epex(self):
        from_utc = int(self.fromdt.astimezone(pytz.utc).timestamp()/60)
        to_utc = int(self.todt.astimezone(pytz.utc).timestamp()/60)
        sql = f"""SELECT
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
                  WHERE tsid = 19 
                  GROUP BY YEAR(localstart), MONTH(localstart)
                ) p
                  ON t.startmonth = p.utcmonth
                WHERE t.utcstart>={from_utc} and t.utcstart < {to_utc}
                ORDER BY t.localstart"""
        return sql

    def evaluate_digital_meter(self, ts_id):
        """
        Evaluate the timeseries based on the provided ts_id.
        """
        # Placeholder for timeseries evaluation logic
        # This should be replaced with actual evaluation logic
        avg_epex_sql = self._get_avg_epex()
        sql = (f"""select m.utcstart,p.price*m.offtake as offtake_cost, p.price*m.injection as injection_cost from 
               ts_digital_meter m join ({avg_epex_sql}) p
               on m.utcstart = p.utcstart
               where m.tsid = {ts_id} and m.utcstart >= {int(self.fromdt.timestamp()/60)} and m.utcstart < {int(self.todt.timestamp()/60)}
               order by m.utcstart""")
        df = self.database.query(sql, timecols=['utcstart'])
        return df

    def evaluate(self):
        from_utc = int(self.fromdt.astimezone(pytz.utc).timestamp()/60)
        to_utc = int(self.todt.astimezone(pytz.utc).timestamp()/60)

        self.evaluate_digital_meter(ts_id=2)
        self.evaluate_digital_meter(ts_id=3)

        df = self.database.query("SELECT * FROM ids_timeseries")
        print(df)

        all_ts = self.edw_api.get_timeseries()


        endex101 = next(filter(lambda x: x.name=="endex/101/15", all_ts), None)
        epex = next(filter(lambda x: x.name=="Epex/BE/15", all_ts), None)
        ean_ts = list(filter(lambda x: x.vaultName == "digital_meter", all_ts))

        epex_data = self.edw_api.get_datapoints(epex, self.fromdt, self.todt)

        print(ean_ts)

ContractTypeEvaluation(datetime.now(pytz.UTC)-timedelta(days=365), datetime.now(pytz.UTC)).evaluate()