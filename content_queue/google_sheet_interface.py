# content_queue/google_sheet_interface.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from api.config import SERVICE_ACCOUNT_FILE, SHEET_NAME, WORKSHEET_NAME

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(credentials)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

def append_row(data):
    sheet.append_row(data)
    print("Row appended:", data)

