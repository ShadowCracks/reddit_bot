import os
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

MESSAGED_FILE = "messaged_authors.txt"

def load_messaged_authors():
    """Load a set of authors from a text file, one username per line."""
    authors_set = set()
    if os.path.exists(MESSAGED_FILE):
        with open(MESSAGED_FILE, "r", encoding="utf-8") as f:
            for line in f:
                username = line.strip()
                if username:
                    authors_set.add(username)
    return authors_set

def append_author_to_file(username):
    """Append a single username to the text file."""
    with open(MESSAGED_FILE, "a", encoding="utf-8") as f:
        f.write(username + "\n")

# A list of alternative openers to spark curiosity
openers = [
    "I checked out your post, sounds right up my alley—would you mind if I asked a few questions?",
    "Hi! I saw your post and thought I might be a good fit. I'd love to learn more if you have a sec.",
    "Hey, your post caught my eye because I’ve got some relevant experience. Want to see if we’re on the same page?",
    "I came across your posting and a creative notion struck me—do you have a moment to hear it?",
    "I’ve got some thoughts on how I might help. Care to discuss for a minute?",
    "Hello! I noticed your ‘hiring’ post and I’m excited about the role. Can u share more details?",
    "Hey! I believe I can bring something unique. Can we chat about the specifics?",
    "Hello there, your post really resonated with me—I’d love to see if we could collaborate. Are you open to a quick conversation?",
    "I have a proposal that’s a bit off the beaten path—mind if I run it by you?"
]

def monitor_job_posts():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=/home/shadow-crack/reddit_bot_chrome_profile")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=chrome_options)

    print("Chrome launched. You have 5 seconds to sign in if needed...")
    time.sleep(5)

    # Load authors we've already messaged from disk
    messaged_authors = load_messaged_authors()
    print(f"Loaded {len(messaged_authors)} authors from {MESSAGED_FILE}.")

    while True:
        try:
            driver.get('https://old.reddit.com/user/ejarkerm/m/job/new/')
            time.sleep(3)

            print("Checking new posts...")
            posts = driver.find_elements(By.CLASS_NAME, "thing")
            print("Number of posts found:", len(posts))

            for post in posts:
                try:
                    # e.g. "[HIRING] We need a dev" 
                    title_element = post.find_element(By.CLASS_NAME, "title")
                    title = title_element.text.strip()

                    # e.g. "someUser123"
                    author_elem = post.find_element(By.CLASS_NAME, "author")
                    author_name = author_elem.text.strip()

                    if "hiring" in title.lower():
                        # Skip if we've already messaged this author
                        if author_name in messaged_authors:
                            print(f"Already messaged '{author_name}', skipping.")
                            continue

                        print(f"Found a 'hiring' post by '{author_name}', sending chat message...")

                        # Navigate to the author's page
                        author_url = author_elem.get_attribute("href")
                        driver.get(author_url)
                        time.sleep(2)

                        # Click the Old Reddit "chat" link
                        chat_button = driver.find_element(
                            By.XPATH, "//a[@data-message-type='navigate.chat']"
                        )
                        chat_button.click()
                        time.sleep(3)

                        # Wait for the chat iframe to appear
                        iframe = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "iframe.pinned-to-bottom.chat-app-window.regular")
                            )
                        )
                        driver.switch_to.frame(iframe)

                        # Wait a bit for the chat input to be ready
                        time.sleep(5)

                        # Select a random opener from our list
                        selected_message = random.choice(openers)
                        
                        # Send keys to the currently focused element
                        active_element = driver.switch_to.active_element
                        active_element.send_keys(selected_message)
                        active_element.send_keys(Keys.ENTER)

                        # Append this author to our persistent file
                        messaged_authors.add(author_name)
                        append_author_to_file(author_name)

                        time.sleep(2)
                        # Switch back to the main document
                        driver.switch_to.default_content()

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
