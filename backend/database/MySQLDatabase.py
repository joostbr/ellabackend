import datetime
import pandas as pd
import mysql.connector
from mysql.connector import pooling
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytz
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
EDW_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE"),
}


class MySQLDatabase:

    _instance = None


    @staticmethod
    def instance():
        if MySQLDatabase._instance is None:
            MySQLDatabase._instance = MySQLDatabase(**EDW_CONFIG)
        return MySQLDatabase._instance

    @staticmethod
    def close_all():
        if MySQLDatabase._instance is not None:
            MySQLDatabase._instance.close()

    def __init__(self, host, user, password, database, port=3306, pool_size=2):
        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._port = port
        self._pool_size = pool_size
        self._engine = None
        self._sessionmaker = None


    @property
    def engine(self):
        if self._engine is None:
            connection_string = (
                f"mysql+pymysql://{self._user}:{self._password}@{self._host}:{self._port}/{self._database}"
            )
            self._engine = create_engine(connection_string, pool_pre_ping=True)
        return self._engine

    @property
    def sessionmaker(self):
        if self._sessionmaker is None:
            self._sessionmaker = sessionmaker(bind=self.engine)
        return self._sessionmaker

    def new_session(self):
        return self.sessionmaker()

    def close(self):
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

    def get_engine(self):
        return self.engine

    def query(self, sql, timecols=None):

        result = pd.read_sql_query(sql, self.engine, parse_dates=timecols)

        return result

    def delete(self, table, where):
        with self.engine.connect() as connection:
            connection.execute(f"DELETE FROM {table} WHERE {where}")
            connection.commit()

    def update(self, table, setclause, where=None):
        with self.engine.connect() as connection:
            query = f"UPDATE {table} SET {setclause}"
            if where is not None:
                query += f" WHERE {where}"
            connection.execute(query)
            connection.commit()

    def execute(self, sql):
        with self.engine.connect() as connection:
            connection.execute(sql)
            connection.commit()

    def update_batch(self, sql, values):
        with self.engine.connect() as connection:
            cursor = connection.connection.cursor(prepared=True)
            cursor.executemany(sql, values)
            connection.commit()

    def bulk_insert(self, df, table='', key_cols=[], data_cols=[], where=None, moddate_col=None):
        """
        Performs a MySQL-style UPSERT using INSERT ... ON DUPLICATE KEY UPDATE
        """
        with self.engine.connect() as connection:
            cursor = connection.connection.cursor()

            # Construct column lists
            all_cols = key_cols + data_cols
            if moddate_col:
                all_cols.append(moddate_col)

            # Create placeholders for values
            placeholders = ','.join(['%s'] * len(all_cols))
            update_clause = ','.join([f"{col}=VALUES({col})" for col in data_cols])
            if moddate_col:
                update_clause += f", {moddate_col}=CURRENT_TIMESTAMP"

            # Construct the query
            sql = f"""
                INSERT INTO {table} ({','.join(all_cols)})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {update_clause}
            """

            # Prepare data
            values = [tuple(row) + (None,) if moddate_col else tuple(row) 
                     for row in df[all_cols if not moddate_col else all_cols[:-1]].values]

            # Execute
            cursor.executemany(sql, values)
            connection.commit()

if __name__ == "__main__":
    # Example usage
    fromdt = datetime.datetime(2022, 11, 1)
    todt = datetime.datetime(2022, 12, 1)
    fromdtlocal = pytz.utc.localize(fromdt)
    todtlocal = pytz.utc.localize(todt)

    db = MySQLDatabase.instance()
    df = db.query("""
        SELECT * FROM ts_prices 
        WHERE tsid=19
    """, timecols=['utc_time'])

    if not df.empty:
        df_range = pd.date_range(
            min(df["utc_time"]), 
            max(df["utc_time"]) + datetime.timedelta(minutes=14),
            freq="1min"
        ).to_frame().rename(columns={0: "utc_time"})
        
        df = df_range.merge(df, how="left", on="utc_time")
        df = df.ffill()
        df["local_time"] = df["utc_time"].dt.tz_convert("Europe/Brussels").dt.tz_localize(None)
        df[["local_time", "price"]].to_excel("epex_mysql.xlsx")

