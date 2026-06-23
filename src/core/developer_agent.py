import os
import subprocess
from pathlib import Path
from src.core.state import ProjectStateManager

class DeveloperAgent:
    def __init__(self, state_manager: ProjectStateManager):
        self.state = state_manager
        
    def read_spec_from_whiteboard(self) -> str:
        """Reads the current contents of the whiteboard to extract the PM spec."""
        if self.state.scratchpad_path.exists():
            return self.state.scratchpad_path.read_text()
        return ""

    def execute_code_generation(self) -> dict:
        """Extracts context from the whiteboard and invokes aider via CLI subprocess."""
        print("💻 Developer Agent: Reading whiteboard instructions...")
        whiteboard_context = self.read_spec_from_whiteboard()
        
        if not whiteboard_context:
            return {"status": "ERROR", "message": "Whiteboard file is empty or missing."}
            
        # Update state to signal code generation is underway
        self.state.update_phase("DEVELOPING", tasks=["Aider code mutation processing..."])
        
        # Build a highly explicit instructions prompt for Aider's CLI execution loop
        aider_prompt = (
            f"You are the DevBand automated code generator. "
            f"Read the following whiteboard specifications carefully and implement the target file. "
            f"Ensure the code is robust and includes basic exception handling.\n\n"
            f"WHITEBOARD SPECIFICATIONS:\n{whiteboard_context}"
        )
        
        print("⚡ Developer Agent: Launching Aider background subprocess loop...")
        
        # We instruct Aider to modify files cleanly without spawning an interactive terminal shell
        command = [
            "uv", "run", "aider",
            "--message", aider_prompt,
            "--no-auto-commits",  # Prevents filling git log with intermediate micro-saves
            "--yes"               # Auto-accepts file changes suggested by Qwen
        ]
        
        try:
            # Execute Aider in headless mode
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✅ Developer Agent: Aider execution finished writing changes to the directory.")
            self.state.update_phase("TESTING", tasks=["Pass context to QA Agent for verification"])
            return {"status": "SUCCESS", "log": result.stdout}

        except FileNotFoundError:
            error_log = (
                "Aider executable not found. Install it with "
                "`uv tool install aider-chat` (or `pip install aider-chat`)."
            )
            print(f"❌ Developer Agent: {error_log}")
            self.state.update_phase("FAILED", tasks=["Install Aider"], logs=error_log)
            return {"status": "FAILED", "message": error_log}

        except subprocess.CalledProcessError as e:
            error_log = f"Aider Subprocess Error:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
            print("❌ Developer Agent: Aider failed to execute code mutation.")
            self.state.update_phase("DEVELOPING", tasks=["Retry code gen"], logs=error_log)
            return {"status": "FAILED", "message": error_log}
