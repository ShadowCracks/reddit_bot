import os
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

MESSAGED_FILE = "messaged_authors.txt"
NO_CHAT_FILE = "no_chat_authors.txt"

# A list of alternative openers for general or fallback cases
openers = [
    "Hey, your post caught my eye because I’ve got some relevant experience. Want to see if we’re on the same page?",
    "I’ve got some thoughts on how I might help. Care to discuss for a minute?",
    "Hello! I noticed your post and I’m excited about the role. Can u share more details?",
    "Hey! I believe I can bring something unique to your project. Can we chat about the specifics?",
    "Hey just read your post. Do you mind if I ask a few questions?"
]

# Messages for specific categories
DESIGN_MESSAGE = (
    "Hey, I'm an experienced logo designer/video editor. I'd love to send you my portfolio "
    "on Discord, Telegram, or via email if you're interested!"
)
DEV_MESSAGE = (
    "Hey! Here’s my portfolio: nofeelance.com. I took a good look at your post, and I'd "
    "love to ask a few more questions about it."
)

# Keywords for specific categories
design_keywords = ["logo design", "video editing"]
dev_keywords = ["developer", "website", "app", "javascript", "typescript", "bot", "automation", "blockchain"]

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

def get_message_for_post(title: str) -> str:
    """
    Returns the message to send based on the post title.
    1. If title contains "logo design" or "video editing" → DESIGN_MESSAGE
    2. If title contains any developer-related keywords → DEV_MESSAGE
    3. If the post *only* contains "hiring" or "task" → random choice from openers
    4. Otherwise, random choice from openers
    """
    lower_title = title.lower().strip()

    # 1. Check design-related keywords
    if any(k in lower_title for k in design_keywords):
        return DESIGN_MESSAGE

    # 2. Check developer-related keywords
    if any(k in lower_title for k in dev_keywords):
        return DEV_MESSAGE

    # 3. If the entire title is just "hiring" or "task"
    if lower_title in ["hiring", "task"]:
        return random.choice(openers)

    # 4. Fallback message
    return random.choice(openers)

def monitor_job_posts():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=/home/shadow-crack/reddit_bot_chrome_profile")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=chrome_options)

    print("Chrome launched. You have 5 seconds to sign in if needed...")
    time.sleep(5)

    # Load authors we've already processed from disk (both messaged and no chat)
    processed_authors = load_processed_authors()
    print(f"Loaded {len(processed_authors)} processed authors from files.")

    while True:
        try:
            driver.get('https://old.reddit.com/user/ejarkerm/m/job/new/')
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

                    # We'll still filter on "hiring" in the title to identify relevant posts,
                    # but the message we send now depends on the new function
                    if "hiring" in title.lower():
                        # Skip if we've already processed
                        if author_name in processed_authors:
                            print(f"Already processed '{author_name}', skipping.")
                            continue

                        print(f"Found a 'hiring' post by '{author_name}', processing...")
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
                                
                                # Decide which message to send based on the post title
                                selected_message = get_message_for_post(title)

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
