import os
from src.core.graph import DevBandOrchestrator

def main():
    # Setup optional model/url switches for Ollama or local endpoint variables
    os.environ["MODEL_NAME"] = "qwen2.5-coder:7b"
    os.environ["LOCAL_LLM_URL"] = "http://localhost:11434/v1/chat/completions"
    
    # Define a clean, explicit hackathon requirement
    hackathon_prompt = (
        "Create a file named fibonacci_tool.py containing a function named 'calculate_fibonacci' "
        "that accepts an integer N and returns a list containing the sequence. "
        "The function must raise a ValueError if N is negative."
    )
    
    # Initialize and fire the state pipeline orchestration
    orchestrator = DevBandOrchestrator()
    orchestrator.run_pipeline(hackathon_prompt)

if __name__ == "__main__":
    main()
