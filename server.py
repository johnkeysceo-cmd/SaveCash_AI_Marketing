from flask import Flask, jsonify
import gspread
import json
import os
import csv
import time
import requests
from threading import Thread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Platform posting functions
from platform_modules.instagram_poster import post_instagram
from platform_modules.threads_poster import post_threads
from platform_modules.x_twitter_semi_auto.approval_listener import post_x_twitter

# AI content generation
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_post(platform, topic, tone="professional"):
    prompt = f"""
    Write a {tone} social media post about "{topic}" for {platform}.
    Include hashtags if applicable. Keep it short and engaging.
    """
    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Flask app
app = Flask(__name__)

# Load Google service account
GOOGLE_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_INFO = json.loads(GOOGLE_JSON)
SHEET_NAME = "SaveCash_Test"
LOG_FILE = "logs/post_logs.csv"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
client = gspread.authorize(credentials)
sheet = client.open(SHEET_NAME).sheet1

@app.route("/")
def home():
    return jsonify({"status": "SaveCash AI Marketing API is running"})

@app.route("/generate-next", methods=["POST"])
def generate_next():
    try:
        topic = "SaveCash AI Marketing Automation"
        platforms = ["Instagram", "Threads", "X"]

        for platform in platforms:
            content = generate_post(platform, topic)
            sheet.append_row([platform, content, "", "pending", 0])  # Add retry_count column

        return jsonify({"success": True, "message": "AI posts generated and added"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/post-next", methods=["POST"])
def post_next():
    try:
        rows = sheet.get_all_records()
        next_post = None
        for idx, row in enumerate(rows):
            if row.get("status", "").lower() in ["", "pending"]:
                next_post = (idx + 2, row)  # +2 because sheet rows start at 1 and header row
                break

        if not next_post:
            return jsonify({"success": False, "message": "No pending posts found"})

        row_number, post = next_post
        platform = post.get("platform").lower()
        content = post.get("content")
        media_url = post.get("media_url", None)
        retry_count = int(post.get("retry_count", 0))

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

        # Retry logic
        if not success and retry_count < 3:
            retry_count += 1
            sheet.update_cell(row_number, sheet.find("retry_count").col, retry_count)
        else:
            sheet.update_cell(row_number, sheet.find("status").col, "posted" if success else "failed")

        # Log the post
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.utcnow().isoformat(), platform, content, success, message, retry_count])

        return jsonify({"success": success, "message": message})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Auto-post loop
def auto_post_loop(interval=3600):
    while True:
        try:
            requests.post(f"{os.getenv('APP_URL')}/post-next")
        except Exception as e:
            print("Auto-post error:", e)
        time.sleep(interval)

Thread(target=auto_post_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

