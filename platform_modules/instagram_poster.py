from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.instagramuser import InstagramUser
import os

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
APP_ID = os.getenv("FACEBOOK_APP_ID")
APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")

FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)

def post_instagram(content, media_url=None):
    """
    Posts a photo + caption to Instagram Business account
    """
    try:
        ig_user = InstagramUser(INSTAGRAM_ACCOUNT_ID)
        data = {
            "caption": content,
            "image_url": media_url
        }
        post = ig_user.create_media(data=data)
        ig_user.create_media_publish({
            "creation_id": post["id"]
        })
        return True, f"Posted to Instagram successfully: {post['id']}"
    except Exception as e:
        return False, str(e)
