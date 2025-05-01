import pandas as pd
import pytz
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from backend.services.edw import EDWApi, DataPoint, TimeSeries
load_dotenv()

class E2XAPI:
    def __init__(self, base_url="https://e2x-vpp-api.cioc-e2x.com"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        self.username = os.getenv("E2X_USER")
        self.password = os.getenv("E2X_PASSWORD")
        self.edw_api = EDWApi()
        self.site_ids = ["EF9904F2", "83325360", "4BE09281"]

    def authenticate(self, username=None, password=None):
        """
        Authenticate with the E2X API and retrieve a JWT token.
        Args:
            username (str): The client's username.
            password (str): The client's password.
        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        url = f"{self.base_url}/auth/token"
        payload = {
            "username": username if username else self.username,
            "password": password if password else self.password
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raises an error for 4xx/5xx responses

            data = response.json()
            self.token = data.get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}"
            }
            return True

        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                print("Authentication failed: Invalid or missing parameters.")
            elif response.status_code == 401:
                print("Authentication failed: Invalid credentials.")
            else:
                print(f"Authentication error: {e}")
            return False
        except Exception as e:
            print(f"Error during authentication: {e}")
            return False

    def get_site_data(self, site_key, fromdt=None, todt=None):
        """
        Retrieve energy information for a specific site.
        Args:
            site_key (str): The ID of the site associated with the BESS.
            quarter_hour (str, optional): UTC timestamp in the format %Y-%m-%dT%H:%M:%SZ.
                                         Example: 2025-01-17T02:00:00Z
        Returns:
            dict: Energy information if successful, None otherwise.
        """
        if not self.token:
            print("Error: You must authenticate first.")
            return None

        url = f"{self.base_url}/energy-info/{site_key}"
        params = {}

        dt = fromdt.astimezone(pytz.utc)
        result = []
        while  dt < todt:
            # "2025-03-28T12:00:00Z"
            params["quarter_hour"] = self.utcformat(dt)

            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()
                data["UTCTIME"] = dt
                result.append(data)
                print("received data for", dt.isoformat())

            except requests.exceptions.HTTPError as e:
                if response.status_code == 400:
                    print("Error: Invalid or missing parameters, or insufficient permissions.")
                    return None
                elif response.status_code == 401:
                    print("Error: Authentication failed. Invalid credentials.")
                    return None
                else:
                    print(f"Error retrieving energy info: {e}")
            except Exception as e:
                print(f"Error during energy info retrieval: {e}")
                return None

            dt = dt + timedelta(minutes=15)

        return pd.DataFrame(result)

    def create_timeseries(self, site_id):
        timeseries = self.edw_api.get_timeseries()
        ts = next(filter(lambda x: x.name == f"cioc/{site_id}", timeseries), None)
        if not ts:
            vault = next(filter(lambda x: x.name== "elion", self.edw_api.get_vaults()), None)
            if vault:
                res = self.edw_api.create_timeseries("cioc/"+site_id, f"cioc", "PT15M", None, None, None, None)
                print("created timeseries", res)
                return res

    def find_or_create_timeseries(self, site_id):
        timeseries = self.edw_api.get_timeseries()
        ts = next(filter(lambda x: x.name == f"cioc/{site_id}", timeseries), None)
        if ts:
            return ts
        else:
            print(f"Timeseries for site {site_id} not found, creating...")
            ts_json = self.create_timeseries(site_id)
            ts_json["firstTime"] = None
            ts_json["lastTime"] = None
            return TimeSeries(**ts_json)

    def utcformat(self, dt):
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def store_data(self, ts, df):
        insert_data = [
            DataPoint(
                start=self.utcformat(row["UTCTIME"]),
                values=[row['Grid_energy_in']/10,
                        row['Grid_energy_out']/10,
                        row['Solar_energy_in']/10 if row['Solar_energy_in'] else 0,
                        row['Battery_energy_in']/10 if row['Battery_energy_in'] else 0,
                        row['Battery_energy_out']/10 if row['Battery_energy_in'] else 0])
            for _, row in df.iterrows()
        ]
        self.edw_api.store_datapoints(ts.id, insert_data)

    def create_timeseries_structure(self):
        """
        Create the timeseries structure in the database.
        """
        # Implement the logic to create the timeseries structure
        '''fields = ["offtake", "injection", "production", "charge", "discharge"]
        fieldspecs = [{"name": x, "type": "DECIMAL", "precision": 9, "scale": 3, "unit": ""} for x in
                      fields]
        self.edw_api.create_recordspec(name='cioc', field_specs=fieldspecs)

        self.edw_api.create_vault("cioc", "cioc", partitioned=False)'''

        for site_id in self.site_ids:
            ts = self.edw_api.create_timeseries(f"cioc/{site_id}", "cioc", "PT15M", None, None, None, None)
            print("created timeseries", ts)

    def run(self):
        if self.authenticate():
            fromutc = datetime.now(pytz.UTC) - timedelta(days=1)
            fromutc = fromutc.replace(hour=0, minute=0, second=0, microsecond=0)
            toutc = datetime.now(pytz.UTC)
            for site_id in self.site_ids:
                ts = self.find_or_create_timeseries(site_id)
                if ts.lastTime is not None:
                    fromutc = ts.lastTime - timedelta(minutes=30)
                print(f"Fetching data for site {site_id} from {fromutc} to {toutc}")
                df = self.get_site_data(site_id, fromutc, toutc)
                self.store_data(ts, df)
        else:
            print("Authentication failed. Cannot run the process.")


# Example usage:
if __name__ == "__main__":
    # Initialize the API client
    api = E2XAPI()

    api.run()