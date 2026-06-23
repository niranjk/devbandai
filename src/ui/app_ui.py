import streamlit as st
import time
from pathlib import Path

# Set up page configurations
st.set_page_config(
    page_title="DevBand AI Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 DevBand AI: Autonomous Multi-Agent Scrum Workspace")
st.caption("Live Tracking Layer • Powered by Band Platform & Qwen 2.5 Coder Local Node")

# Sidebar configurations for input controls
st.sidebar.header("🚀 Hackathon Engine Control")
raw_input_text = st.sidebar.text_area(
    "Enter Feature Requirement Token:",
    value="Create a file named fibonacci_tool.py containing a function named 'calculate_fibonacci' that accepts an integer N and returns a list containing the sequence. The function must raise a ValueError if N is negative.",
    height=150
)

# Anchor paths for live parsing
SCRATCHPAD_PATH = Path(".scratchpad.md").resolve()
CODE_PATH = Path("fibonacci_tool.py").resolve()

def parse_whiteboard():
    """Reads and parses the live file state machine."""
    if not SCRATCHPAD_PATH.exists():
        return "INITIALIZATION", [], "Waiting for orchestrator ignition sequence..."
        
    try:
        content = SCRATCHPAD_PATH.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        phase = "INITIALIZATION"
        tasks = []
        logs_started = False
        log_lines = []
        
        for line in lines:
            if "- Active Phase:" in line:
                phase = line.split("Active Phase:")[-1].strip()
            elif "- [ ]" in line or "- [x]" in line:
                tasks.append(line.replace("- [ ]", "⏳").replace("- [x]", "✅").strip())
            elif "## Execution Logs" in line:
                logs_started = True
                continue
            
            if logs_started:
                log_lines.append(line)
                
        return phase, tasks, "\n".join(log_lines).strip()
    except Exception as e:
        return "ERROR", [], f"Read block alert: {str(e)}"

# Layout Grid Split
col_left, col_right = st.columns([1, 1])

with col_left:
    st.header("🔄 Real-Time Agent Orchestration")
    
    # Live Parse Call
    phase, tasks, logs = parse_whiteboard()
    
    # Dynamic Status Indicators
    if phase == "PLANNING":
        st.info("📋 Active Node: PRODUCT MANAGER AGENT (Analyzing Requirements)")
    elif phase == "DEVELOPING":
        st.warning("💻 Active Node: DEVELOPER AGENT (Executing Aider Subprocess)")
    elif phase == "TESTING":
        st.error("🧪 Active Node: QA AUTOMATION ENGINEER (Running Unit Test Suites)")
    elif phase == "COMPLETED":
        st.success("🏆 Pipeline Target Cleared: Verified Production Artifact Available!")
    else:
        st.subheader(f"⚙️ Status: {phase}")

    # Task Breakdown Display
    st.subheader("📋 Active Sprint Backlog Tasks")
    if tasks:
        for t in tasks:
            st.markdown(f"#### {t}")
    else:
        st.write("*No operational tasks inside active workspace window.*")

    # Output Console Terminal Display
    st.subheader("🖥️ Agent System Execution Logs")
    st.code(logs if logs else "Awaiting task logs...", language="text")

with col_right:
    st.header("📄 Generated Code Workspace View")
    
    if CODE_PATH.exists():
        try:
            code_content = CODE_PATH.read_text(encoding="utf-8")
            st.code(code_content, language="python")
            st.caption(f"📍 Location: {CODE_PATH}")
        except Exception:
            st.info("Reading file buffer lock...")
    else:
        st.info("⏳ Code Asset View Empty. Awaiting Developer Agent code creation pass...")

# Auto-refresh loop mechanism to keep the dashboard updating in real-time
time.sleep(1)
st.rerun()
