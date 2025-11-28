from platform_modules.instagram_poster import post_instagram
from platform_modules.threads_poster import post_threads
from platform_modules.x_twitter_semi_auto.approval_listener import post_x_twitter
from content_queue.google_sheet_interface import get_pending_posts, update_post_status

def process_pending_posts():
    posts = get_pending_posts()  # Should return a list of dicts with keys: Row, Platform, Content, Media_URL
    results = []

    for post in posts:
        platform = post['Platform'].lower()
        content = post['Content']
        media_url = post.get('Media_URL', None)
        row_number = post['Row']

        try:
            if platform == "instagram":
                success, msg = post_instagram(content, media_url)
            elif platform == "threads":
                success, msg = post_threads(content, media_url)
            elif platform in ["x", "twitter"]:
                success, msg = post_x_twitter(content, media_url)
            else:
                success, msg = False, "Unknown platform"

            update_post_status(row_number, success, msg)
            results.append({"row": row_number, "platform": platform, "success": success, "message": msg})

        except Exception as e:
            update_post_status(row_number, False, str(e))
            results.append({"row": row_number, "platform": platform, "success": False, "message": str(e)})

    return results

