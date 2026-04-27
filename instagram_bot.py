from google import genai
import os
import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
# It is recommended to use environment variables for security
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BUFFER_ACCESS_TOKEN = os.environ.get("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILE_ID = os.environ.get("BUFFER_PROFILE_ID") # The ID of your Instagram profile in Buffer

def generate_instagram_post(niche="High-Protein Indian Meals"):
    """Generates a caption and image prompt using Gemini 2.0 Flash."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Create a highly engaging Instagram post for the brand 'ViroqDaily' about {niche}.
    The goal is to provide value and then drive engagement with a hook.
    
    Include:
    1. A catchy headline.
    2. 3-4 bullet points of high-value information.
    3. A clear Call to Action (CTA): "Comment 'PLAN' to get my 7-day meal prep guide."
    4. 5-10 relevant hashtags.
    5. A short description of an ideal image to go with this post.
    
    Format the output as JSON with keys: 'caption' and 'image_prompt'.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    try:
        # Clean up the response text in case Gemini adds markdown code blocks
        text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return None

def post_to_buffer(caption, image_url=None):
    """Pushes the content to Buffer for scheduling/posting."""
    url = "https://api.bufferapp.com/1/updates/create.json"
    
    payload = {
        'profile_ids': [BUFFER_PROFILE_ID],
        'text': caption,
        'shorten': False,
        'now': True # Set to False if you want it to go into the regular Buffer queue
    }
    
    if image_url:
        payload['media[photo]'] = image_url

    headers = {
        'Authorization': f'Bearer {BUFFER_ACCESS_TOKEN}'
    }

    response = requests.post(url, data=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    if not all([GEMINI_API_KEY, BUFFER_ACCESS_TOKEN, BUFFER_PROFILE_ID]):
        print("Missing API keys or Profile ID. Please set environment variables.")
    else:
        print(f"Generating post for ViroqDaily at {datetime.now()}...")
        post_data = generate_instagram_post()
        
        if post_data:
            print("Post generated successfully.")
            print(f"Caption: {post_data['caption'][:50]}...")
            
            # Note: For a fully automated image, you'd integrate a tool like 
            # Midjourney, DALL-E, or Canva API here to get an 'image_url'.
            # For now, we post the caption.
            
            # result = post_to_buffer(post_data['caption'])
            # print(f"Buffer API Response: {result}")
            result = post_to_buffer(post_data['caption'])
            print(f"Buffer API Response: {result}")
            print("\nNext step: Connect an image generation API or use a template URL to 'post_to_buffer'.")
