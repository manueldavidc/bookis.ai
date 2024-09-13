import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def moderate_content(text):
    try:
        response = openai_client.moderations.create(input=text)
        result = response.results[0]

        # Allow mild content, focus on more serious issues
        serious_categories = [
            "violence", "sexual", "hate", "self-harm", "sexual/minors"
        ]

        for category in serious_categories:
            if getattr(result.categories, category):
                return False

        return True
    except Exception as e:
        print(f"Error in content moderation: {e}")
        return False
