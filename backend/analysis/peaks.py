from datetime import datetime, timedelta
from backend.services.edw import DataPoint, TimeSeries, EDWApi
from backend.database.MySQLDatabase import MySQLDatabase
from backend.core.statistics import Statistics, StatisticsRepository
import pandas as pd
import pytz

class PeakAnalysis:

    def __init__(self):
        self.edw_api = EDWApi()
        self.database = MySQLDatabase.instance()
        self.statistics_repo = StatisticsRepository()

    def analyze_peaks(self):
        sql = """WITH last_12_months AS (
                SELECT DATE_FORMAT(DATE_SUB(CONVERT_TZ(NOW(), 'UTC', 'Europe/Brussels'), INTERVAL n MONTH), '%%Y-%%m-01') AS first_day
                FROM (
                    SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3
                    UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL
                    SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
                    UNION ALL SELECT 11 union all select 12 
                ) AS nums
            ),
            monthly_peaks AS (
                SELECT
                    dm.tsid,
                    DATE_FORMAT(dm.localstart, '%%Y-%%m') AS month,
                    MAX(dm.offtake) AS peak_offtake
                FROM edw.ts_digital_meter dm
                WHERE dm.localstart >= (SELECT MIN(first_day) FROM last_12_months)
                GROUP BY dm.tsid, month
            ),
            peak_rows AS (
                SELECT
                    dm.tsid,
                    DATE_FORMAT(dm.localstart, '%%Y-%%m-01') AS month,
                    dm.localstart AS peak_timestamp,
                    dm.offtake
                FROM edw.ts_digital_meter dm
                JOIN monthly_peaks mp
                    ON dm.tsid = mp.tsid
                    AND DATE_FORMAT(dm.localstart, '%%Y-%%m') = mp.month
                    AND dm.offtake = mp.peak_offtake
            )
            SELECT tsid, month, MAX(offtake) AS peak_offtake, MIN(peak_timestamp) AS peak_timestamp
            FROM peak_rows
            GROUP BY tsid, month
            ORDER BY tsid, month DESC;
            """
        df = self.database.query(sql=sql)
        print(df)

    def analyze(self):
        # Implement visualization logic
        self.analyze_peaks()

if __name__ == "__main__":

    e = PeakAnalysis()
    e.analyze()
