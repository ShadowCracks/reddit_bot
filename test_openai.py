
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    if not api_key:
        print("OPENAI_API_KEY not set in environment variables.")
        return
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say hello!"}
            ],
            max_completion_tokens=256
        )
        print("OpenAI API test successful!")
        print("Model used:", model)
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print("OpenAI API test failed:", e)

if __name__ == "__main__":
    test_openai()
