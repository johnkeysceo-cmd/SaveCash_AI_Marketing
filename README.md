# SaveCash_AI_Marketing Starter Repo

## Setup Instructions
1. Install Python 3.11+
2. Navigate to the `api/` folder
3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
4. Make sure `savecash-service.json` is in `api/`
5. Run test:
    ```
    python test_sheets.py
    ```
6. If a row appears in Google Sheets, setup works!

## Usage
- Generate text: `python content_generation/generate_text.py`
- Generate prompts: `python content_generation/generate_prompts.py`
- Generate dummy images/videos: `python visual_video_creation/generate_images.py`
- Add post to queue: `from content_queue.post_queue import add_to_queue`

