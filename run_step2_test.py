from src.core.pm_agent import ProductManagerAgent

def main():
    agent = ProductManagerAgent()
    prompt = "Create a simple calculation function that returns the Fibonacci sequence up to N numbers"
    agent.process_prompt(prompt)

if __name__ == '__main__':
    main()
