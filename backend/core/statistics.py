from backend.core.repository import Repository
from sqlalchemy import Column, BigInteger, String, Integer, DECIMAL, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import text
import pandas as pd



Base = declarative_base()

class Statistics(Base):
    __tablename__ = 'nett.statistics'
    __table_args__ = {'schema': 'nett'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    siteid = Column(String(100), nullable=True)
    tsid = Column(Integer, ForeignKey('edw.ids_timeseries.id', ondelete='CASCADE'), nullable=True)
    value = Column(DECIMAL(9, 3), nullable=True)
    description = Column(String(256), nullable=True)
    calculationtime = Column(DateTime, nullable=True)
    fromutc = Column(DateTime, nullable=True)
    toutc = Column(DateTime, nullable=True)
    statkey = Column(String(100), nullable=False)
    eventtimeutc = Column(DateTime, nullable=True)



class StatisticsRepository(Repository):
    def __init__(self):
        """Initialize StatisticsRepository by inheriting Repository."""
        super().__init__()

    def find_by_timeseries(self, tsid: int):
        """Fetch all statistics records as a list of Statistics objects."""
        with self.new_session() as session:
            return session.query(Statistics).filter(Statistics.tsid == tsid).all()

    def find_by_timeseries(self, siteid: str):
        """Fetch all statistics records as a list of Statistics objects."""
        with self.new_session() as session:
            return session.query(Statistics).filter(Statistics.tsid == siteid).all()


    def find_between(self, tsid, start_time, end_time):
        """Fetch all statistics records for a given tsid between start and end time."""
        with self.new_session() as session:
            return session.query(Statistics).filter(
                Statistics.tsid == tsid,
                Statistics.fromutc >= start_time,
                Statistics.toutc < end_time
            ).all()

    def find_between_as_df(self, tsid, start_time, end_time):
        """Fetch all statistics records for a given tsid between start and end time as a DataFrame."""
        with self.new_session() as session:
            query = session.query(Statistics).filter(
                Statistics.tsid == tsid,
                Statistics.fromutc >= start_time,
                Statistics.toutc < end_time
            )
            return pd.read_sql_query(query.statement, session.bind)

    def bulk_upsert(self, data):
        """Bulk insert or update statistics records."""
        with self.new_session() as session:
            val = session.execute(
                text("""
                INSERT INTO nett.statistics (siteid, tsid, value, description, calculationtime, fromutc, toutc, statkey, eventtimeutc)
                VALUES (:siteid, :tsid, :value, :description, :calculationtime, :fromutc, :toutc, :statkey, :eventtimeutc)
                ON DUPLICATE KEY UPDATE
                    value = VALUES(value),
                    description = VALUES(description),
                    calculationtime = VALUES(calculationtime),
                    fromutc = VALUES(fromutc),
                    toutc = VALUES(toutc),
                    eventtimeutc = VALUES(eventtimeutc)
                """),
                data
            )
            print(val.rowcount)
            session.commit()
            return len(data)
