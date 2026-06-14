import os
import sys
import streamlit as st

# Ensure the root package is visible to the UI runner
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.graph import hackathon_engine
from src.core.state import HackathonState

# Set page styling parameters
st.set_page_config(page_title="AI Hackathon Starter Kit", page_icon="🏆", layout="wide")

st.title("🏆 Stateful AI Hackathon Orchestrator")
st.subheader("Powered by LangGraph, Python, uv & Hugging Face")
st.markdown("---")

# User Input Panel
user_prompt = st.text_area(
    "What autonomous application do you want to blueprint today?",
    placeholder="e.g., Build an autonomous AI agent that tracks gas fees on Ethereum and alerts users via Discord.",
    height=100
)

if st.button("🚀 Execute Map-Reduce Agentic Chain", type="primary"):
    if not user_prompt.strip():
        st.warning("Please enter a valid engineering goal first!")
    else:
        with st.spinner("🧠 Orchestrating nodes... Calling Hugging Face Serverless APIs..."):
            try:
                # Fire up the backend engine we built in Phase 2
                initial_state = HackathonState(input_query=user_prompt)
                final_state = hackathon_engine.invoke(initial_state)
                
                # Render the final output beautifully using markdown structures
                st.success("✨ Execution Complete!")
                st.markdown("### 📊 Compiled Master Blueprint")
                st.write(final_state.get("final_output", "No response generated."))
                
            except Exception as e:
                st.error(f"❌ Critical Pipeline Failure: {str(e)}")
