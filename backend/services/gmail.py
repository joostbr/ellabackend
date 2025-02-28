import os
from os import getenv
import base64
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Gmail API Scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

class GmailService:

    def __init__(self):
        pass

    def authenticate_gmail(self):
        """Authenticate and return Gmail API service."""
        creds = None

        # Load token if exists
        if os.path.exists("./data/gmail_token.json"):
            creds = Credentials.from_authorized_user_file("./data/gmail_token.json", SCOPES)

        # If no valid credentials, request login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("./data/gmail_credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open("gmail_token.json", "w") as token:
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def send_email(self, to_email, subject, html_body):
        """Send an email using Gmail API."""
        service = self.authenticate_gmail()

        # Create email message
        msg = MIMEMultipart()
        msg["to"] = to_email
        msg["subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        # Encode message
        raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        message = {"raw": raw_msg}

        # Send email
        service.users().messages().send(userId="me", body=message).execute()
        print(f"✅ Email sent to {to_email}")

# Example Usage
# GmailService().send_email("user@amplifino.com", "Hello from Gmail API", "This is a test email sent via Gmail API.")
