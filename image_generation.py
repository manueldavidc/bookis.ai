import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_images(prompts, age):
    image_urls = []
    try:
        style = "bright, colorful, and cartoony" if 4 <= age <= 8 else "realistic and detailed"
        for prompt in prompts:
            full_prompt = f"A children's book illustration in a {style} style. {prompt}"
            response = openai_client.images.generate(
                prompt=full_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response.data[0].url
            image_urls.append(image_url)
        return image_urls
    except Exception as e:
        print(f"Error generating images: {e}")
        return None
