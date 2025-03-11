import pandas as pd
from sqlalchemy import Column, Integer, DECIMAL, TIMESTAMP, Computed
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

from backend.core.repository import Repository

Base = declarative_base()

class TimeSeriesPrice(Base):
    __tablename__ = "ts_prices"

    tsid = Column(Integer, primary_key=True)
    utcstart = Column(Integer, primary_key=True)
    recordtime = Column(TIMESTAMP, nullable=False, server_default=func.now())
    price = Column(DECIMAL(7,2), nullable=False)

    def __repr__(self):
        return f"<TimeSeriesPrice(tsid={self.tsid}, utcstart={self.utcstart}, price={self.price})>"

    @hybrid_property
    def utcstart_as_datetime(self):
        """Convert utcstart (minutes since 1970) to a Python datetime (UTC)."""
        return func.from_unixtime(self.utcstart * 60)

    @utcstart_as_datetime.expression
    def utcstart_as_datetime(cls):
        """SQLAlchemy expression to convert utcstart in SQL."""
        return func.from_unixtime(cls.utcstart * 60)

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
