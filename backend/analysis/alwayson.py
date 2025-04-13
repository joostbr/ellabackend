import pandas as pd
from astral.sun import sun
from astral import LocationInfo
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from backend.services.edw import EDWApi
from backend.core.statistics import Statistics, StatisticsRepository
import pytz

class AlwaysOn:

    def __init__(self, fromdt, todt):
        self.fromdt = fromdt
        self.todt = todt
        self.edw_api = EDWApi()
        self.statistics_repo = StatisticsRepository()

    def get_night_periods(self):
        # Set location: Brussels, Belgium
        location = LocationInfo("Brussels", "Belgium", "Europe/Brussels", 50.8503, 4.3517)
        timezone = pytz.timezone(location.timezone)

        timestamps = pd.date_range(start=self.fromdt, end=self.todt, freq='15min', tz=timezone)
        df = pd.DataFrame({'timestamp': timestamps})

        # Determine night hours for each timestamp
        def is_night(ts):
            s = sun(location.observer, date=ts.date(), tzinfo=timezone)
            return ts < s['sunrise'] or ts > s['sunset']

        df['is_night'] = df['timestamp'].apply(is_night)

        # Filter night periods
        night_df = df[df['is_night'] == True]

        # Save or return night timestamps
        print(night_df.head())

        return night_df

    def analyze_digital_meter(self, ts, night_periods):
        datapoints = self.edw_api.get_datapoints(ts, self.fromdt, self.todt)
        flat_list = [[x['start']]+ x['values'] for x in datapoints]
        df = pd.DataFrame(flat_list, columns=["startutc"]+ts.fieldNames)
        df["UTCTIME"] = pd.to_datetime(df["startutc"], utc=True)
        df["TIME"] = df["UTCTIME"].dt.tz_convert("Europe/Brussels")
        if df["injection"].sum()>0: # if we have production (assuming solar here)
            df = df.join(night_periods.set_index("timestamp"), on="UTCTIME", how="inner") # filter on non solar periods
        df["MONTH"]=df["TIME"].dt.to_period("M")
        df.set_index("TIME", inplace=True)
        monthly_min = df[['MONTH','offtake']].groupby('MONTH').min()
        monthly_min['month_start'] = monthly_min.index.to_timestamp()
        print(monthly_min)
        return monthly_min

    def store_statistics(self, ts, df):
        stats = []
        for index, row in df.iterrows():
            stat = Statistics(
                siteid="00000",
                tsid=ts.id,
                value=row["offtake"]*4,
                description="Minimal Offtake (kW)",
                calculationtime=datetime.now(),
                fromutc=pytz.timezone("Europe/Brussels").localize(row["month_start"]).astimezone(pytz.utc),
                toutc= pytz.timezone("Europe/Brussels").localize(row["month_start"]+pd.DateOffset(months=1)).astimezone(pytz.utc),
                statkey="minimal/offtake",
                eventtimeutc=None
            )
            stats.append(stat)
        self.statistics_repo.bulk_upsert([s.__dict__ for s in stats])


    def analyze(self):
        night_periods = self.get_night_periods()

        all_ts = self.edw_api.get_timeseries()

        ean_ts = list(filter(lambda x: x.vaultName == "digital_meter", all_ts))
        for each in ean_ts:
            print(ean_ts)
            df = self.analyze_digital_meter(ts=each, night_periods=night_periods)
            self.store_statistics(ts=each, df=df)


if __name__ == "__main__":
    nowdt = datetime.now(pytz.timezone("Europe/Brussels"))
    fromdt = nowdt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)-relativedelta(months=12)
    todt = nowdt
    analysis = AlwaysOn(fromdt, todt)
    analysis.analyze()