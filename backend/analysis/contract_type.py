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

    def evaluate(self):

        df = self.database.query("SELECT * FROM ids_timeseries")
        print(df)

        all_ts = self.edw_api.get_timeseries()


        endex101 = next(filter(lambda x: x.name=="endex/101/15", all_ts), None)
        epex = next(filter(lambda x: x.name=="Epex/BE/15", all_ts), None)
        ean_ts = list(filter(lambda x: x.vaultName == "digital_meter", all_ts))

        epex_data = self.edw_api.get_datapoints(epex, self.fromdt, self.todt)

        print(ean_ts)

ContractTypeEvaluation(datetime.now(pytz.UTC)-timedelta(days=365), datetime.now(pytz.UTC)).evaluate()