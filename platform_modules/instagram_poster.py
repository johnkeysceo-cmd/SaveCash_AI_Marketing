# platform_modules/instagram_poster.py

def post_instagram(content, media_url=None):
    """
    Stub function to post to Instagram.
    Replace this with real API calls using Meta Graph API.
    
    Returns: success(bool), message(str)
    """
    try:
        # Example debug print
        print(f"[Instagram] Posting: {content} | Media: {media_url}")

        # TODO: Replace with actual Instagram API call here
        # Example: using Graph API to publish content
        # success = instagram_api.post(content, media_url)

        success = True  # Mock success
        message = "Instagram post simulated successfully"
        return success, message

    except Exception as e:
        return False, str(e)
