from google.oauth2.service_account import Credentials
from app.services.google_sheets import GoogleSheetsService
import base64
import json

# Load the credentials from the base64 encoded file
with open("app/credentials/credentials.b64", "r") as file:
    encoded_credentials = file.read()
info = json.loads(base64.b64decode(encoded_credentials))

creds = Credentials.from_service_account_info(
    info,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)

sheets_service = GoogleSheetsService(creds)


def get_google_sheets_service():
    return sheets_service
