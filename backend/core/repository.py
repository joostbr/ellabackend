import pandas as pd
from backend.database.MySQLDatabase import MySQLDatabase
class Repository:

    def __init__(self):
        self._database = MySQLDatabase.instance()

    @property
    def database(self):
        return self._database

    def new_session(self):
        return self.database.new_session()


