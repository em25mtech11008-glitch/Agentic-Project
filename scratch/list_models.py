import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("API Key begins with:", api_key[:10] if api_key else "None")

try:
    client = genai.Client(api_key=api_key)
    print("Listing models...")
    for m in client.models.list():
        print(f"- {m.name} (supported actions: {m.supported_actions})")
except Exception as e:
    import traceback
    traceback.print_exc()
