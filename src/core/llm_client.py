import httpx
from huggingface_hub import InferenceClient
from src.config import Config

class HackathonLLM:
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        
        # Initialize the free Hugging Face serverless client
        if self.provider == "huggingface":
            if not Config.HF_TOKEN:
                raise ValueError("HF_TOKEN is missing from your environment variables!")
            self.client = InferenceClient(token=Config.HF_TOKEN)
            
        # Placeholders for easy future integration during a hackathon
        elif self.provider == "openai":
            # self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            pass

    def generate(self, prompt: str, system_instruction: str = "You are a helpful AI assistant.") -> str:
        """Universal text generation function."""
        
        if self.provider == "huggingface":
            messages = [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
            # Calls the free serverless inference API effortlessly
            response = self.client.chat_completion(
                model=Config.HF_MODEL,
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content
            
        elif self.provider == "openai":
            # Drop-in your quick code for OpenAI when needed
            return "OpenAI Integration Placeholder"
            
        else:
            raise NotImplementedError(f"Provider '{self.provider}' is not configured yet.")
