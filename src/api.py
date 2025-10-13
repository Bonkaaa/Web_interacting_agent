import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    return genai.client(
        api_key=os.environ.get("GENAI_API_KEY")
    )



