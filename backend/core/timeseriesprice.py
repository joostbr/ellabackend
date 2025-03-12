import pandas as pd
from sqlalchemy import Column, Integer, DECIMAL, TIMESTAMP, DATETIME, Computed
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func, text
from sqlalchemy.orm import column_property

from backend.core.repository import Repository

Base = declarative_base()

class TimeSeriesPrice(Base):
    __tablename__ = "ts_prices"

    tsid = Column(Integer, primary_key=True)
    utcstart = Column(Integer, primary_key=True, name='utcstart')
    recordtime = Column(TIMESTAMP, nullable=False, server_default=func.now())
    price = Column(DECIMAL(7,2), nullable=False)
    utcstart_dt = column_property(func.from_unixtime(utcstart * 60))

    def __repr__(self):
        return f"<TimeSeriesPrice(tsid={self.tsid}, utcstart={self.utcstart}, price={self.price})>"



class TimeSeriesPriceRepository(Repository):
    def __init__(self):
        """Initialize TimeSeriesPriceRepository by inheriting Repository."""
        super().__init__()

    def find_by_timeseries(self, tsid):
        """Fetch all time-series price records as a list of TimeSeriesPrice objects."""
        with self.new_session() as session:
            return session.query(TimeSeriesPrice).filter(TimeSeriesPrice.tsid == tsid).all()

    def find_between(self, tsid, start_time, end_time):
        """Fetch all price records for a given tsid between start and end time."""
        with self.new_session() as session:
            return session.query(TimeSeriesPrice).filter(
                TimeSeriesPrice.tsid == tsid,
                TimeSeriesPrice.utcstart >= start_time.timestamp() // 60,
                TimeSeriesPrice.utcstart < end_time.timestamp() // 60
            ).all()


    def find_between_as_df(self, tsid, start_time, end_time):
        """Fetch all price records for a given tsid between start and end time."""
        with self.new_session() as session:
            query = session.query(TimeSeriesPrice).filter(
                TimeSeriesPrice.tsid == tsid,
                TimeSeriesPrice.utcstart >= start_time.timestamp() // 60,
                TimeSeriesPrice.utcstart < end_time.timestamp() // 60
            )
            return pd.read_sql_query(query.statement, session.bind)

    def bulk_upsert(self, data):
        with self.new_session() as session:
            val = session.execute(
                text("""
                INSERT INTO ts_prices (tsid, utcstart, price, recordtime)
                VALUES (:tsid, :utcstart, :price, :recordtime)
                ON DUPLICATE KEY UPDATE price = VALUES(price), recordtime = VALUES(recordtime)
                """),
                data
            )
            print(val.rowcount)
            session.commit()
            return len(data)