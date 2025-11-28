# content_queue/post_queue.py
queue = []

def add_to_queue(post_data):
    queue.append(post_data)
    print("Post added to queue:", post_data)

