from datetime import datetime
import pandas as pd
import pytz
from backend.core.statistics import Statistics, StatisticsRepository
from datetime import datetime, timedelta
from backend.services.edw import EDWApi
from backend.database.MySQLDatabase import MySQLDatabase

class InjectionAnalysis:
    """
    Analyze and persist statistics about injected energy during negative vs positive prices.
    """

    def __init__(self, fromdt: datetime, todt: datetime):
        self.fromdt = fromdt
        self.todt = todt
        self.edw_api = EDWApi()
        self.database = MySQLDatabase.instance()
        self.statistics_repo = StatisticsRepository()

    def _get_timeseries(self):
        all_ts = self.edw_api.get_timeseries()
        epex = next(filter(lambda x: x.name == "Epex/BE/15", all_ts), None)
        digital_meters = list(filter(lambda x: x.vaultName == "digital_meter", all_ts))
        return digital_meters, epex

    def _build_query(self, ts, price_ts):
        sql = f"""
        SELECT 
            from_unixtime(m.utcstart * 60) AS timestamp,
            m.injection,
            p.price
        FROM 
            ts_digital_meter m
        JOIN 
            ts_prices p ON m.utcstart = p.utcstart
        WHERE 
            m.tsid = {ts.id}
            AND p.tsid = {price_ts.id}
            AND m.utcstart >= {int(self.fromdt.timestamp() / 60)}
            AND m.utcstart < {int(self.todt.timestamp() / 60)}
        ORDER BY m.utcstart
        """
        return sql

    def analyze(self, persist=True):
        digital_meters, price_ts = self._get_timeseries()
        for ts in digital_meters:
            if not ts or not price_ts:
                raise Exception("Required timeseries not found.")

            sql = self._build_query(ts, price_ts)
            df = self.database.query(sql=sql, timecols=['timestamp'])

            if df.empty:
                print("No data found for the selected period.")
                return pd.DataFrame()

            # Convert UTC to Europe/Brussels
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert('Europe/Brussels')
            df.set_index('timestamp', inplace=True)
            df['month'] = df.index.to_period('M')

            df['positive_injection'] = df.apply(lambda x: x['injection'] if x['price'] >= 0 else 0, axis=1)
            df['negative_injection'] = df.apply(lambda x: x['injection'] if x['price'] < 0 else 0, axis=1)

            summary = df.groupby('month')[['positive_injection', 'negative_injection']].sum()
            summary['total_injection'] = summary['positive_injection'] + summary['negative_injection']
            summary['neg_price_pct'] = (summary['negative_injection'] / summary['total_injection']) * 100
            summary.fillna(0, inplace=True)
            if persist:
                self._persist_statistics(summary, ts.id)


    def _persist_statistics(self, summary_df: pd.DataFrame, tsid: int):
        import pytz
        from pandas import Timestamp

        now = datetime.utcnow()
        brussels_tz = pytz.timezone("Europe/Brussels")
        stats_to_insert = []

        for period, row in summary_df.iterrows():
            # Convert Period to timestamp in Brussels time
            month_start_local = period.to_timestamp().tz_localize(brussels_tz)
            month_end_local = (period + 1).to_timestamp().tz_localize(brussels_tz)

            # Convert to UTC for DB storage
            fromutc = month_start_local.astimezone(pytz.UTC)
            toutc = month_end_local.astimezone(pytz.UTC)


            stats_to_insert.extend([
                Statistics(
                    siteid="00000",
                    tsid=tsid,
                    statkey='injection/pos_priced',
                    value=row['positive_injection'],
                    description='Injected kWh with positive price',
                    calculationtime=now,
                    fromutc=fromutc,
                    toutc=toutc,
                    eventtimeutc=None
                ),
                Statistics(
                    siteid="00000",
                    tsid=tsid,
                    statkey='injection/neg_priced',
                    value=row['negative_injection'],
                    description='Injected kWh with negative price',
                    calculationtime=now,
                    fromutc=fromutc,
                    toutc=toutc,
                    eventtimeutc=None
                ),
                Statistics(
                    siteid="00000",
                    tsid=tsid,
                    statkey='injection/neg_price_pct',
                    value=row['neg_price_pct'],
                    description='Percentage of injected kWh at negative price',
                    calculationtime=now,
                    fromutc=fromutc,
                    toutc=toutc,
                    eventtimeutc=None
                )
            ])

        self.statistics_repo.bulk_upsert([s.__dict__ for s in stats_to_insert])
        print(f"✅ Persisted {len(stats_to_insert)} injection statistics.")

if __name__ == "__main__":


    # Example usage
    analysis = InjectionAnalysis(
        fromdt=datetime.now(pytz.timezone("Europe/Brussels")) - timedelta(days=365),
        todt=datetime.now(pytz.timezone("Europe/Brussels")),
    )
    result = analysis.analyze()
    print(result)