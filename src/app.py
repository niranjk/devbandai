import sys
from src.core.graph import hackathon_engine
from src.core.state import HackathonState

def run_pipeline(user_goal: str):
    print("🚀 Initializing Stateful LangGraph Engine...")
    
    # Initialize the starting state
    initial_state = HackathonState(input_query=user_goal)
    
    # Execute the graph
    print("🧠 Mapping and Reducing tasks via Hugging Face Serverless API...")
    final_state = hackathon_engine.invoke(initial_state)
    
    print("\n================== 🏆 FINAL COMPREHENSIVE OUTPUT ==================\n")
    print(final_state["final_output"])
    print("\n===================================================================\n")

if __name__ == "__main__":
    # Test query or use command-line args
    query = "Build an autonomous AI agent that tracks gas fees on Ethereum and alerts users via Discord."
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        
    run_pipeline(query)
