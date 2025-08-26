import os
import random
import time
import json
from openai import OpenAI
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MESSAGED_FILE = "messaged_authors.txt"
NO_CHAT_FILE = "no_chat_authors.txt"


# Initialize OpenAI client
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    import os
    import json
    from openai import OpenAI
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    MESSAGED_FILE = "messaged_authors.txt"
    NO_CHAT_FILE = "no_chat_authors.txt"

    # Initialize OpenAI client
    try:
        client = OpenAI()
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        print("Make sure your OPENAI_API_KEY is set.")
        exit(1)

    def load_processed_authors():
        """Load a set of processed authors from both messaged and no-chat files."""
        authors_set = set()
        for filename in [MESSAGED_FILE, NO_CHAT_FILE]:
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        username = line.strip()
                        if username:
                            authors_set.add(username)
        return authors_set

    def append_author_to_file(username):
        """Append a single username to the messaged file."""
        with open(MESSAGED_FILE, "a", encoding="utf-8") as f:
            f.write(username + "\n")

    def append_no_chat_author_to_file(username):
        """Append a single username to the no chat file."""
        with open(NO_CHAT_FILE, "a", encoding="utf-8") as f:
            f.write(username + "\n")

    def analyze_post_with_ai(full_post_text: str) -> dict:
        """
        Use OpenAI to analyze if a post is software development related and generate a response.
        """
        try:
            prompt = (
                f"Is this post someone HIRING a SOFTWARE DEVELOPER/PROGRAMMER for coding work?\n"
                f"Post: \"{full_post_text}\"\n"
                "ONLY respond if they need someone to WRITE CODE, build software, create apps, or do programming work.\n"
                "Do NOT respond to: Video editors, graphic designers, content creators, people offering services or selling products, general tech discussions or non-coding jobs, any non-programming work.\n"
                "IMPORTANT: If this is a hiring post for coding work, your message MUST: Be 2-3 sentences max, sound casual, creative, and original, be funny, sassy, and cool, show you understood what they're looking for (briefly mention the project/tech), write in first person (I/me) as a confident freelance developer, if it's app development (mobile apps): mention 'vastcom.us', if it's other software development: mention 'nofeelance.com'.\n"
                "Examples of good messages: React e-commerce? Been there, crushed that. I live and breathe JSX - check out my playground at nofeelance.com. Mobile apps are my jam! I've launched more iOS/Android apps than I can count. Peep my work at vastcom.us. Python automation is literally my superpower. I make scripts so smooth they practically write themselves - nofeelance.com.\n"
                "If NOT hiring for programming/coding: return empty message.\n"
                "Return JSON: { 'is_hiring_post': true/false, 'message': 'your response OR empty string' }"
            )
            response = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a confident, badass freelance developer who knows their craft inside out. Be creative, funny, sassy, and cool. GRAB ATTENTION with your personality while showing you're the expert they need. Sound like a boss, not a corporate drone."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,
                max_completion_tokens=3000
            )
            response_content = response.choices[0].message.content
            print(f"Raw AI response: {response_content}")
            if response_content.strip().startswith("```json"):
                response_content = response_content.strip().replace("```json", "").replace("```", "").strip()
            elif response_content.strip().startswith("```"):
                response_content = response_content.strip().replace("```", "").strip()
            try:
                result = json.loads(response_content)
                return result
            except json.JSONDecodeError as json_err:
                print(f"JSON parsing error: {json_err}")
                print(f"Response was not valid JSON: {response_content}")
                return {"is_hiring_post": False, "message": ""}
        except Exception as e:
            print(f"Error with AI analysis: {e}")
            print(f"Full error details: {type(e).__name__}: {str(e)}")
            return {"is_hiring_post": False, "message": ""}
                # Delay between subreddits
