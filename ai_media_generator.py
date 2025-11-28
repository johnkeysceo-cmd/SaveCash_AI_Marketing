import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_image(prompt):
    """
    Generates an image URL using OpenAI DALL·E API.
    """
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']
