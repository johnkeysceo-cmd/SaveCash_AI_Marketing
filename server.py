from flask import Flask, jsonify
import gspread
import json
import os
import csv
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Import your platform posting functions
from platform_modules.instagram_poster import post_instagram
from platform_modules.threads_poster import post_threads
from platform_modules.x_twitter_semi_auto.approval_listener import post_x_twitter

app = Flask(__name__)

# Load service account JSON from environment
GOOGLE_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_INFO = json.loads(GOOGLE_JSON)

SHEET_NAME = "SaveCash_Test"
LOG_FILE = "logs/post_logs.csv"

# Google Sheets setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
client = gspread.authorize(credentials)
sheet = client.open(SHEET_NAME).sheet1

@app.route("/")
def home():
    return jsonify({"status": "SaveCash AI Marketing API is running"})

@app.route("/post-next", methods=["POST"])
def post_next():
    try:
        rows = sheet.get_all_records()
        
        # Find the first pending post
        next_post = None
        for idx, row in enumerate(rows):
            if row.get("status", "").lower() in ["", "pending"]:
                next_post = (idx + 2, row)  # +2 because sheet rows start at 1 and header row
                break

        if not next_post:
            return jsonify({"success": False, "message": "No pending posts found"})

        row_number, post = next_post
        platform = post.get("platform", "").lower()
        content = post.get("content", "")
        media_url = post.get("media_url", None)

        # Post to the appropriate platform
        success = False
        message = ""
        if platform == "instagram":
            success, message = post_instagram(content, media_url)
        elif platform == "threads":
            success, message = post_threads(content, media_url)
        elif platform in ["x", "twitter"]:
            success, message = post_x_twitter(content, media_url)
        else:
            message = f"Unknown platform: {platform}"

        # Update Google Sheet status
        status_col = sheet.find("status").col
        sheet.update_cell(row_number, status_col, "posted" if success else "failed")

        # Log the post
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.utcnow().isoformat(), platform, content, success, message])

        return jsonify({"success": success, "message": message})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
