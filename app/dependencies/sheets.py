from google.oauth2.service_account import Credentials
from app.services.google_sheets import GoogleSheetsService

creds = Credentials.from_service_account_file(
    "app/credentials/credentials.json",
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)

sheets_service = GoogleSheetsService(creds)


def get_google_sheets_service():
    return sheets_service
