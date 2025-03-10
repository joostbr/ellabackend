import pdfplumber
import pandas as pd
import re
import os
import requests
import numpy as np
import pytz

from backend.database.MySQLDatabase import MySQLDatabase
from datetime import datetime

DATA_FOLDER = "data"  # Folder to save downloaded PDF file

class EndexDownloader:

    def __init__(self):
        self.database = MySQLDatabase.instance()

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

            if len(endex_df)>0:
                # Save to CSV and get DataFrame
                endex_df.to_csv(os.path.join(DATA_FOLDER,"endex_data.csv"), index=False)

                # Display a sample of the data
                print("\nSample of parsed data (first 5 rows):")
                print(endex_df.head())

                # Optionally, filter and show only Endex 101 values
                print("\nEndex 101 values only (first 5 rows):")
                print(endex_df[["Month", "Endex101"]].head())
            else:
                print("Failed to parse Endex values from the extracted text.")
        else:
            print("Failed to extract text from the PDF.")


if __name__ == "__main__":
    EndexDownloader().run()