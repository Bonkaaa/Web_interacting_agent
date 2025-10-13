import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

def get_llm():
    """
    Initialize and return the Google Gemini LLM instance.
    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance.
    """
    llm = ChatGoogleGenerativeAI(
        model = os.environ.get("MODEL_NAME", "gemini-2.5-pro"),
        temperature=0.2,
        max_output_tokens=512,
        top_k=40,
        convert_system_message_to_human = True,
        google_api_key = os.environ.get("GOOGLE_API_KEY")
    )
    return llm

if __name__ == "__main__":
    llm = get_llm()
    print("LLM initialized:", llm)



