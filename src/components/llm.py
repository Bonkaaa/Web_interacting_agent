import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama


load_dotenv()

def get_llm():
    """
    Initialize and return the Google Gemini LLM instance.
    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance.
    """
    llm = ChatOllama(
        model="gpt-oss:20b",
        temperature=0.7,
        num_predict=512,
        validate_model_on_init=True,
    )
    return llm

if __name__ == "__main__":
    llm = get_llm()
    print("LLM initialized:", llm)



