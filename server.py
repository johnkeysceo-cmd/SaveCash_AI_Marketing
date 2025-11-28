from flask import Flask, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

SERVICE_ACCOUNT_FILE = "service_account/savecash-service.json"
SHEET_NAME = "SaveCash_Test"

@app.route("/")
def home():
    return jsonify({"status": "SaveCash AI Marketing API is running"})


@app.route("/test-google", methods=["GET"])
def test_google():
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, scope
        )
        client = gspread.authorize(credentials)
        sheet = client.open(SHEET_NAME).sheet1

        sheet.append_row(["Render Deployed!", "Success"])

        return jsonify({"success": True, "message": "Row appended to Google Sheet"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
