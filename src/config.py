import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    # Default to Hugging Face, but easily switchable via .env
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "huggingface").lower()
    
    # API Keys
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Target Models
    HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
