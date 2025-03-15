import os

import pytz
import requests
import base64
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

SITE_IDS = [343] # kiosun

load_dotenv()

class Elion:

    def __init__(self, site_ids=SITE_IDS):
        self.token = self.get_token()
        self.site_ids = site_ids

    def get_token(self):

        username = os.getenv("ELION_USER")
        password = os.getenv("ELION_PASSWORD")
        auth_credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(auth_credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }

        url = "https://api-interface.elion.be/login"

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            print("Login successful!")
            return response.json()["access_token"]
        else:
            print(f"Failed with status code {response.status_code}")
            print("Response:", response.text)

    def get_data(self, token, method, params):
        url = f"https://api-interface.elion.be{method}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.status_code, response.text)

    def post_data(self, token, method, site_id, data):
        url = f"https://api-interface.elion.be{method}"

        params = {"site_id": site_id}

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        body = data

        response = requests.post(url, headers=headers, params=params, json=body)
        return response

    def get_site_data(self, site_id, fromutc: datetime, touc: datetime):
        fromutc_str = fromutc.strftime("%Y-%m-%d %H:%M")
        toutc_str = touc.strftime("%Y-%m-%d %H:%M")
        grid_data = pd.DataFrame(self.get_data(self.token, "/box_data/grid_metering_box", {
            "fromutc": fromutc_str,
            "touc": toutc_str,
            "time_format": "%Y-%m-%d %H:%M",
            "site_id": site_id,
            #"granularity": "15"??
        })["GRID_DATA"])
        grid_data["UTCTIME"] = pd.to_datetime(grid_data["UTCTIME"])

        cons_data = pd.DataFrame(self.get_data(self.token, "/box_data/total_consumption", {
            "fromutc": fromutc_str,
            "touc": toutc_str,
            "time_format": "%Y-%m-%d %H:%M",
            "site_id": site_id,
        })["CONSUMPTION_DATA"])
        cons_data["UTCTIME"] = pd.to_datetime(cons_data["UTCTIME"])
        cons_data = cons_data.drop(columns=['CONSUMPTION_CUMULATIVE'])


        prod_data = pd.DataFrame(self.get_data(self.token, "/box_data/total_production", {
            "fromutc": fromutc_str,
            "touc": toutc_str,
            "time_format": "%Y-%m-%d %H:%M",
            "site_id": site_id,
        })["PRODUCTION_DATA"])
        prod_data["UTCTIME"] = pd.to_datetime(prod_data["UTCTIME"])
        prod_data = prod_data.drop(columns=['PRODUCTION_CUMULATIVE'])

        prod_curt_data = pd.DataFrame(self.get_data(self.token, "/box_data/curtailed_production", {
            "fromutc": fromutc_str,
            "touc": toutc_str,
            "time_format": "%Y-%m-%d %H:%M",
            "site_id": site_id,
        })["PRODUCTION_DATA"])
        prod_curt_data["UTCTIME"] = pd.to_datetime(prod_curt_data["UTCTIME"])
        prod_curt_data = prod_curt_data.rename(columns={"PRODUCTION": "CURTAILED_PRODUCTION"})
        prod_curt_data = prod_curt_data.drop(columns=['PRODUCTION_CUMULATIVE'])

        prod_uncurt_data = pd.DataFrame(self.get_data(self.token, "/box_data/uncurtailed_production", {
            "fromutc": fromutc_str,
            "touc": toutc_str,
            "time_format": "%Y-%m-%d %H:%M",
            "site_id": site_id,
        })["PRODUCTION_DATA"])
        prod_uncurt_data["UTCTIME"] = pd.to_datetime(prod_uncurt_data["UTCTIME"])
        prod_uncurt_data = prod_uncurt_data.rename(columns={"PRODUCTION": "UNCURTAILED_PRODUCTION"})
        prod_uncurt_data = prod_uncurt_data.drop(columns=['PRODUCTION_CUMULATIVE'])

        flex_data = pd.DataFrame(self.get_data(self.token, "/box_data/charge_discharge", {
            "fromutc": fromutc_str,
            "touc": toutc_str,
            "time_format": "%Y-%m-%d %H:%M",
            "site_id": site_id,
        })["FLEX_DATA"])
        flex_data["UTCTIME"] = pd.to_datetime(flex_data["UTCTIME"])

        soc_data = pd.DataFrame(self.get_data(self.token, "/box_data/soc", {
            "fromutc": "2025-01-01 00:00",
            "touc": "2025-01-02 00:00",
            "time_format": "%Y-%m-%d %H:%M",
            "site_id": site_id,
        })["SOC_DATA"])
        soc_data["UTCTIME"] = pd.to_datetime(soc_data["UTCTIME"])

        df = pd.merge(grid_data, cons_data, on="UTCTIME")
        df = pd.merge(df, prod_data, on="UTCTIME")
        df = pd.merge(df, prod_curt_data, on="UTCTIME")
        df = pd.merge(df, prod_uncurt_data, on="UTCTIME")
        df = pd.merge(df, flex_data, on="UTCTIME")
        df = pd.merge(df, soc_data, on="UTCTIME")

        print("df",df)

        return df

    def store_data(self, site_id, df):
        ts_id = self.find_timeseries_id(site_id)
        insert_data = [
            {
                'tsid': ts_id,
                'utcstart': int(row['UTCTIME'].timestamp() // 60),
                'grid_offtake': row['GRID_OFFTAKE'],
                'grid_inject': row['GRID_INJECT'],
                'consumption': row['CONSUMPTION'],
                'production': row['PRODUCTION'],
                'curtailed_production': row['CURTAILED_PRODUCTION'],
                'uncurtailed_production': row['UNCURTAILED_PRODUCTION'],
                'charge': row['CHARGE'],
                'discharge': row['DISCHARGE'],
                'soc': row['SOC'],
                'recordtime': datetime.now()
            }
            for _, row in df.iterrows()
        ]

    def run(self):
        fromutc = datetime.now(pytz.UTC)-timedelta(days=30)
        toutc = datetime.now(pytz.UTC)
        for site_id in self.site_ids:
            print(site_id)
            self.get_site_data(site_id, fromutc, toutc)



e = Elion()
e.run()