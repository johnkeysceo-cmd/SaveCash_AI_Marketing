import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_post(platform, topic, tone="professional"):
    """
    Generate a social media post for a specific platform.
    """
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
