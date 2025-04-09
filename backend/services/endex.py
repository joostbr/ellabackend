import pdfplumber
import pandas as pd
import re
import os
import requests
import numpy as np
import pytz

from backend.database.MySQLDatabase import MySQLDatabase
from backend.core.timeseriesprice import TimeSeriesPriceRepository
from backend.services.edw import DataPoint, TimeSeries, EDWApi

from datetime import datetime

DATA_FOLDER = "data"  # Folder to save downloaded PDF file

class EndexDownloader:

    def __init__(self):
        self.database = MySQLDatabase.instance()
        self.edw_api = EDWApi()

    def download_pdf(self, url, pdf_file):
        """Download the PDF file from the URL to the local path."""
        try:

            # Download the file
            headers = {"User-Agent": "Mozilla/5.0"}  # Mimic a browser to avoid blocks
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()  # Check for HTTP errors

            # Save the file
            with open(pdf_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"PDF downloaded successfully to {pdf_file}")
            return True
        except requests.RequestException as e:
            print(f"Error downloading PDF: {e}")
            return False

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from all pages of a PDF file."""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
            return full_text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None


    def parse_endex_values(self, text):
        """Parse Endex 101 and 103 values from the extracted text."""
        if not text:
            return None

        # Split the text into lines
        lines = text.strip().split("\n")

        # Initialize list to store data
        data = []

        # Regular expression to match table rows
        # Matches: "$MM / YYYY$ | value | value" or "$MM / YYYY$ | |"
        row_pattern = re.compile(r"(\d{2}/\d{4})\s*([\d,]*)\s*([\d,]*)\s*")

        # Process each line
        for line in lines:
            match = row_pattern.search(line)
            if match:
                month = match.group(1)  # e.g., "01 / 2022"
                endex_101 = match.group(2).replace(",", ".") if match.group(2) else ""  # Replace comma with period
                endex_103 = match.group(3).replace(",", ".") if match.group(3) else ""  # Replace comma with period

                if endex_101 and endex_103:
                    data.append({
                        "Month": pytz.timezone("Europe/Brussels").localize(datetime.strptime('01/'+month,f"%d/%m/%Y")),
                        "Endex101": np.float64(endex_101),
                        "Endex103": np.float64(endex_103)
                    })

        # Convert to DataFrame
        df = pd.DataFrame(data)
        return df


    def save_to_database(self, df):

        df.set_index('Month', inplace=True)

        # Step 2: Expand to 15-minute intervals with repeated values

        start_date = df.index.min()
        end_date = df.index.max() + pd.offsets.MonthEnd(0) + pd.Timedelta(days=1) - pd.Timedelta(minutes=15) # Full last month
        time_range = pd.date_range(start=start_date, end=end_date, freq='15min', tz='Europe/Brussels')
        df_15min = df.reindex(time_range).ffill()
        df_15min.reset_index(inplace=True)
        df_15min.rename(columns={'index': 'Timestamp'}, inplace=True)
        df_15min["UTCTIME"] = df_15min["Timestamp"].dt.tz_convert('UTC')

        # For Endex101

        ts_endex101 = self.find_or_create_timeseries("101")

        insert_data_101 = [
            DataPoint(
                start= row["UTCTIME"],
                values= [row['Endex101'] ]
            )
            for _, row in df_15min.iterrows()
        ]

        self.edw_api.store_datapoints(ts_endex101.id, insert_data_101)

        # For Endex103

        ts_endex103 = self.find_or_create_timeseries("103")

        self.edw_api.store_datapoints(ts_endex101.id, insert_data_101)

        insert_data_103 = [
            DataPoint(
                start=row["UTCTIME"],
                values=[row['Endex103']]
            )
            for _, row in df_15min.iterrows()
        ]

        self.edw_api.store_datapoints(ts_endex103.id, insert_data_103)

        print("Data successfully saved to ts_prices table.")


    def create_timeseries(self, ts_name):
        timeseries = self.edw_api.get_timeseries()

        ts = next(filter(lambda x: x.name == ts_name, timeseries), None)
        if not ts:
            res = self.edw_api.create_timeseries(ts_name, "prices", "PT15M", None, None, None, None)
            print("created timeseries", res)
            return res

    def find_or_create_timeseries(self, endex_code: str):
        timeseries = self.edw_api.get_timeseries()
        ts_name = f"endex/{endex_code}/15"
        ts = next(filter(lambda x: x.name == ts_name, timeseries), None)
        if ts:
            return ts
        else:
            print(f"Timeseries for endex {endex_code} not found, creating...")
            ts_json = self.create_timeseries(ts_name)
            ts_json["firstTime"] = None
            ts_json["lastTime"] = None
            return TimeSeries(**ts_json)



    def run(self):

        pdf_url = "https://www.creg.be/sites/default/files/assets/Tarifs/ElectricityQuotations-NL.pdf"

        # Create data folder if not exists
        os.makedirs(DATA_FOLDER, exist_ok=True)

        local_pdf_file = os.path.join(DATA_FOLDER,"endex_data.pdf")
        self.download_pdf(pdf_url, local_pdf_file)

        print(f"Extracting Endex 101 values from {local_pdf_file} as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Extract text from the PDF
        pdf_text = self.extract_text_from_pdf(local_pdf_file)

        if pdf_text:
            # Parse the values from the extracted text
            endex_df = self.parse_endex_values(pdf_text)
            # Save it to the database
            self.save_to_database(endex_df)
        else:
            print("Failed to extract text from the PDF.")


if __name__ == "__main__":
    e = EndexDownloader()
    e.run()


