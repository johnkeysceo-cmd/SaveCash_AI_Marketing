from flask import Flask, jsonify
import gspread
import json
import os
import csv
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from threading import Thread
import time

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

# === Helpers ===

def get_next_pending_post():
    """Find the next pending post in the Google Sheet."""
    rows = sheet.get_all_records()
    for idx, row in enumerate(rows):
        if row.get("status", "").strip().lower() in ["", "pending"]:
            return idx + 2, row  # +2: header + 1-based index
    return None, None

def update_post_status(row_number, status):
    """Update status in the sheet."""
    try:
        col = sheet.find("status").col
        sheet.update_cell(row_number, col, status)
    except Exception as e:
        print(f"Failed to update sheet: {e}")

def log_post(platform, content, success, message):
    """Log post to CSV file."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat(), platform, content, success, message])

def execute_post(post):
    """Post content to the correct platform."""
    platform = post.get("platform", "").strip().lower()
    content = post.get("content", "")
    media_url = post.get("media_url", None)
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
    
    return platform, content, success, message

# === Endpoints ===

@app.route("/")
def home():
    return jsonify({"status": "SaveCash AI Marketing API is running"})

@app.route("/post-next", methods=["POST"])
def post_next():
    try:
        row_number, post = get_next_pending_post()
        if not post:
            return jsonify({"success": False, "message": "No pending posts found"})

        platform, content, success, message = execute_post(post)
        update_post_status(row_number, "posted" if success else f"failed: {message}")
        log_post(platform, content, success, message)
        
        return jsonify({"success": success, "message": message})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# === Automatic Scheduler ===

def auto_post(interval=300):
    """Automatically post every `interval` seconds."""
    while True:
        row_number, post = get_next_pending_post()
        if post:
            platform, content, success, message = execute_post(post)
            update_post_status(row_number, "posted" if success else f"failed: {message}")
            log_post(platform, content, success, message)
            print(f"[Auto] Posted to {platform}: {content[:30]}... Success={success}")
        time.sleep(interval)  # Wait before checking for next post

# Start auto-posting in a background thread
thread = Thread(target=auto_post, args=(300,), daemon=True)
thread.start()

# === Run App ===

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

