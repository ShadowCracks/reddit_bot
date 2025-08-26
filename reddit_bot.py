def send_simple_chat_message(driver, message):
    """Waits 20 seconds, then types and sends a chat message assuming input is focused."""
    import time
    from selenium.webdriver.common.keys import Keys
    time.sleep(20)
    driver.switch_to.active_element.send_keys(message)
    driver.switch_to.active_element.send_keys(Keys.ENTER)
    print("Message sent!")
import os
import random
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from openai import OpenAI

MESSAGED_FILE = "messaged_authors.txt"
NO_CHAT_FILE = "no_chat_authors.txt"

# Load environment variables if .env file exists
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Initialize OpenAI client
# Make sure to set your OpenAI API key: export OPENAI_API_KEY="your-api-key-here"
# Or run setup_openai.py to set it up
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Make sure your OPENAI_API_KEY is set. Run setup_openai.py to configure it.")
    exit(1)

# A list of alternative openers for fallback cases
openers = [
    "Hey, your post caught my eye because I've got some relevant experience. Want to see if we're on the same page?",
    "I've got some thoughts on how I might help. Care to discuss for a minute?",
    "Hello! I noticed your post and I'm excited about the role. Can you share more details?",
    "Hey! I believe I can bring something unique to your project. Can we chat about the specifics?",
    "Hey just read your post. Do you mind if I ask a few questions?"
]

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

def type_like_human(element, text, wpm=70):
    """
    Simulate human-like typing by sending one character at a time.
    
    Args:
        element: The web element where text is to be typed.
        text (str): The message to type.
        wpm (int): Words per minute speed.
    """
    # Assume an average word length of 5 characters.
    delay = 60.0 / (wpm * 5)  # delay per character in seconds
    for char in text:
        element.send_keys(char)
        # Add slight random variation to mimic natural typing variability.
        time.sleep(delay * random.uniform(0.8, 1.2))


def analyze_post_with_ai(full_post_text: str) -> dict:
    """
    Use OpenAI to analyze if a post is software development related and generate a response.
    
    Returns:
        dict: {
            "is_hiring_post": bool,
            "message": str
        }
    """
    try:
        prompt = f"""
        Is this post someone HIRING a SOFTWARE DEVELOPER/PROGRAMMER for coding work? 

        Post: "{full_post_text}"

        ONLY respond if they need someone to WRITE CODE, build software, create apps, or do programming work.
        Do NOT respond to:
        - Video editors, graphic designers, content creators
        - People offering services or selling products
        - General tech discussions or non-coding jobs
        - Any non-programming work

        IMPORTANT: If this is a hiring post for coding work, your message MUST:
        - Be 2-3 sentences max
        - Sound casual, creative, and original - GRAB THEIR ATTENTION!
        - Be funny, sassy, and cool - sound like a boss who knows their shit
        - Show you understood what they're looking for (briefly mention the project/tech)
        - Write in first person (I/me) as a confident freelance developer
        - If it's app development (mobile apps): mention "vastcom.us"
        - If it's other software development: mention "nofeelance.com"
        
        Examples of good messages:
        "React e-commerce? Been there, crushed that. I live and breathe JSX - check out my playground at nofeelance.com"
        "Mobile apps are my jam! I've launched more iOS/Android apps than I can count. Peep my work at vastcom.us"
        "Python automation is literally my superpower. I make scripts so smooth they practically write themselves - nofeelance.com"
        
        If NOT hiring for programming/coding: return empty message

        {{
            "is_hiring_post": true/false,
            "message": "your response OR empty string"
        }}
        """
        
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL"),
            messages=[
                {"role": "system", "content": "You are a confident, badass freelance developer who knows their craft inside out. Be creative, funny, sassy, and cool. GRAB ATTENTION with your personality while showing you're the expert they need. Sound like a boss, not a corporate drone."},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
            max_completion_tokens=3000
        )
        
        # Parse the JSON response
        response_content = response.choices[0].message.content
        print(f"Raw AI response: {response_content}")
        
        # Strip markdown code blocks if present
        if response_content.strip().startswith("```json"):
            response_content = response_content.strip()
            response_content = response_content.replace("```json", "").replace("```", "").strip()
        elif response_content.strip().startswith("```"):
            response_content = response_content.strip()
            response_content = response_content.replace("```", "").strip()
        
        try:
            result = json.loads(response_content)
            return result
        except json.JSONDecodeError as json_err:
            print(f"JSON parsing error: {json_err}")
            print(f"Response was not valid JSON: {response_content}")
            return {
                "is_hiring_post": False,
                "message": ""
            }
        
    except Exception as e:
        print(f"Error with AI analysis: {e}")
        print(f"Full error details: {type(e).__name__}: {str(e)}")
        # Fallback
        return {
            "is_hiring_post": False,
            "message": ""
        }

def get_message_for_post(full_post_text: str) -> str:
    """
    Use AI to analyze the post and generate an appropriate response.
    """
    analysis = analyze_post_with_ai(full_post_text)
    
    if analysis["is_hiring_post"]:
        print(f"AI identified as hiring post")
        return analysis["message"]
    else:
        print(f"Not a hiring post")
        return ""

def monitor_job_posts():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=/home/shadow-crack/reddit_bot_chrome_profile")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=chrome_options)

    print("Chrome launched. You have 5 seconds to sign in if needed...")
    time.sleep(10)

    # Load authors we've already processed (both messaged and no chat)
    processed_authors = load_processed_authors()
    print(f"Loaded {len(processed_authors)} processed authors from files.")

    while True:
        try:
            driver.get('https://old.reddit.com/user/gemini_caroline/m/job/new/')
            time.sleep(3)

            print("Checking new posts...")
            posts = driver.find_elements(By.CLASS_NAME, "thing")
            print("Number of posts found:", len(posts))

            for post in posts:
                try:
                    title_element = post.find_element(By.CLASS_NAME, "title")
                    title = title_element.text.strip()

                    author_elem = post.find_element(By.CLASS_NAME, "author")
                    author_name = author_elem.text.strip()

                    # Attempt to extract the self-text of the post
                    try:
                        body_element = post.find_element(By.CSS_SELECTOR, ".usertext-body")
                        body_text = body_element.text.strip()
                    except:
                        body_text = ""

                    # Combine title + body
                    full_post_text = f"{title} {body_text}".strip()

                    # Skip if we've already processed
                    if author_name in processed_authors:
                        print(f"Already processed '{author_name}', skipping.")
                        continue

                    # Analyze ALL posts with AI
                    print(f"Found post by '{author_name}'. Analyzing with AI...")
                    print(f"Post title: {title}")
                    print(f"Post body: {body_text[:200]}{'...' if len(body_text) > 200 else ''}")
                    print(f"Full text being sent to AI: {full_post_text[:300]}{'...' if len(full_post_text) > 300 else ''}")
                    
                    analysis = analyze_post_with_ai(full_post_text)
                    
                    if not analysis["is_hiring_post"]:
                        print(f"Not a hiring post for '{author_name}', skipping.")
                        processed_authors.add(author_name)
                        append_no_chat_author_to_file(author_name)
                        continue
                    
                    print(f"AI confirmed hiring post by '{author_name}'. Checking for chat...")

                    author_url = author_elem.get_attribute("href")
                    driver.get(author_url)
                    time.sleep(2)
                    
                    # Check for chat button
                    chat_buttons = driver.find_elements(By.XPATH, "//a[@data-message-type='navigate.chat']")
                    if chat_buttons:
                        print(f"Chat option available for '{author_name}', sending message...")
                        chat_button = chat_buttons[0]
                        chat_button.click()
                        time.sleep(3)
                        
                        try:
                            # Switch to chat iframe
                            iframe = WebDriverWait(driver, 15).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "iframe.pinned-to-bottom.chat-app-window.regular")
                                )
                            )
                            driver.switch_to.frame(iframe)
                            time.sleep(5)
                            
                            # Use the message from AI analysis
                            selected_message = analysis["message"]

                            # Type out the message in a "human-like" way
                            active_element = driver.switch_to.active_element
                            type_like_human(active_element, selected_message)
                            active_element.send_keys(Keys.ENTER)

                            # Switch back out of iframe
                            driver.switch_to.default_content()

                            processed_authors.add(author_name)
                            append_author_to_file(author_name)
                        except Exception as e:
                            print(f"Error processing chat for '{author_name}': {e}")
                            processed_authors.add(author_name)
                            append_author_to_file(author_name)
                    else:
                        print(f"No chat option available for '{author_name}', marking as no chat.")
                        processed_authors.add(author_name)
                        append_no_chat_author_to_file(author_name)
                        
                        time.sleep(2)
                except Exception as e:
                    print(f"Error processing post: {e}")
                    continue

            print("Waiting 1 minute before next check...")
            time.sleep(60)

        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    try:
        monitor_job_posts()
    except KeyboardInterrupt:
        print("\nStopping monitor...")