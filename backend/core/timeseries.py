import pandas as pd
import pytz
from datetime import datetime
from backend.database.MySQLDatabase import MySQLDatabase
from backend.core.repository import Repository
from backend.core.timeseriesprice import TimeSeriesPriceRepository, TimeSeriesPrice

from sqlalchemy import (
    Column, Integer, String, ForeignKey, TIMESTAMP
)
from sqlalchemy.sql import delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TimeSeries(Base):
    __tablename__ = "ids_timeseries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False, unique=True)
    vaultid = Column(Integer, nullable=False)
    interval_length = Column(Integer, nullable=False)
    chronounit = Column(Integer, nullable=False)
    firsttime = Column(Integer, nullable=False)
    lasttime = Column(Integer, nullable=False)
    customer = Column(String(80), nullable=True)
    cluster = Column(String(80), nullable=True)
    category = Column(String(80), nullable=True)
    kind = Column(String(80), nullable=True)
    section = Column(String(80), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    modified_at = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return f"<Timeseries(id={self.id}, name={self.name}, vaultid={self.vaultid})>"


class TimeSeriesRepository(Repository):
    def __init__(self):
        """Initialize TimeSeriesRepository by inheriting Repository."""
        super().__init__()

    def find_by_name(self, name):
        """Fetch a timeseries entry by name."""
        with self.new_session() as session:
            return session.query(TimeSeries).filter(TimeSeries.name == name).first()

    def find_all(self):
        """Fetch all timeseries records as a Pandas DataFrame."""
        with self.new_session() as session:
            result = session.query(TimeSeries).all()
        return result

    def insert_timeseries(self, name, vaultid, interval_length, chronounit, firsttime, lasttime):
        """Insert a new timeseries entry into the database."""
        with self.new_session() as session:
            new_timeseries = TimeSeries(
                name=name,
                vaultid=vaultid,
                interval_length=interval_length,
                chronounit=chronounit,
                firsttime=firsttime,
                lasttime=lasttime,
            )
            session.add(new_timeseries)
            session.commit()
            return new_timeseries

    def delete_by_name(self, name):
        """Delete a timeseries entry by name without querying first."""
        with self.new_session() as session:
            stmt = delete(TimeSeries).where(TimeSeries.name == name)
            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0

def main():

   res = TimeSeriesRepository().find_all()
   print(res)

   res = TimeSeriesPriceRepository().find_by_timeseries(20)
   res = TimeSeriesPriceRepository().find_between_as_df(20, pytz.timezone("Europe/Brussels").localize(datetime(2025,1,1)), pytz.timezone("Europe/Brussels").localize(datetime(2025,2,1)))
   print(res)


if __name__ == "__main__":
    main()