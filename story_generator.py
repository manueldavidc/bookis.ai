import json
import logging
from openai import OpenAI
import os

logging.basicConfig(level=logging.DEBUG)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_title(story_content):
    prompt = f"""
    Based on the following story, generate a short, catchy title for a children's book:

    {story_content}

    The title should be appealing to children and reflect the main theme or characters of the story.
    """
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50
    )
    title = completion.choices[0].message.content
    return title.strip()

def generate_story(educational_objective, age, characters, setting, book_length):
    length_mapping = {
        'short': '5-10',
        'medium': '11-20',
        'long': '21-30'
    }
    page_range = length_mapping[book_length]

    prompt = f"""
    Generate a child-friendly story for a {age}-year-old with the following details:
    Educational Objective: {educational_objective}
    Characters: {characters}
    Setting: {setting}
    Book Length: {page_range} pages

    Important guidelines:
    1. Focus on the theme of friendship and kindness.
    2. Ensure the content is age-appropriate and positive.
    3. Include gentle life lessons without being preachy.
    4. Avoid any scary, violent, or overly complex themes.
    5. Use simple language suitable for a {age}-year-old.
    6. Make the story engaging, fun, and educational.
    7. Incorporate the educational objective seamlessly into the story.
    8. For each paragraph of the story, provide an image description that captures the essence of that part of the story.
    9. Alternate between story paragraphs and image descriptions.
    10. Each page should contain one paragraph and one image description.

    Format the output as a JSON array of objects, where each object represents a page with 'text' and 'image_description' properties.

    The story should be approximately {page_range} pages long.
    """
    
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        story_content = completion.choices[0].message.content
        
        logging.debug("Raw API response: %s", completion)
        logging.debug("Received story content: %s", story_content)

        if not story_content:
            logging.error("Received empty story content from API.")
            raise ValueError("Received empty story content from API.")

        try:
            story_pages = json.loads(story_content)
        except json.JSONDecodeError as e:
            logging.error("Failed to decode JSON: %s", e)
            logging.error("Raw content causing the error: %s", story_content)
            raise

        title = generate_title(story_content)
        return title, story_pages
    except Exception as e:
        logging.error("Error in generate_story: %s", e)
        raise
