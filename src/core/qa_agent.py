import os
import subprocess
from pathlib import Path
from src.core.llm_client import LocalQwenClient
from src.core.state import ProjectStateManager

class QAGerAgent:
    def __init__(self, state_manager: ProjectStateManager, llm_client: LocalQwenClient):
        self.state = state_manager
        self.llm = llm_client
        self.test_file_path = Path("test_target_output.py")
        
    def get_system_prompt(self) -> str:
        return (
            "You are an elite QA Automation Engineer Agent.\n"
            "Your job is to read a technical specification and write a complete, executable Python test script.\n"
            "The test script MUST use the standard 'unittest' framework.\n"
            "It must import the function from the target file and run assertions against it based on the test cases.\n"
            "Output ONLY the raw executable python code block. Do not write markdown blocks like ```python. Just the code."
        )

    def generate_and_save_test_suite(self) -> str:
        """Reads the whiteboard and writes a corresponding unittest file."""
        print("🧪 QA Agent: Reading whiteboard to generate test cases...")
        whiteboard_context = self.state.scratchpad_path.read_text() if self.state.scratchpad_path.exists() else ""
        
        test_code = self.llm.generate_response(
            system_prompt=self.get_system_prompt(),
            user_prompt=f"Generate a unittest file for this specification:\n{whiteboard_context}"
        )
        
        # Clean up any accidental markdown wrapper artifacts from the LLM response
        clean_code = test_code.replace("```python", "").replace("```", "").strip()
        self.test_file_path.write_text(clean_code)
        print(f"📝 QA Agent: Test suite generated and saved to {self.test_file_path}")
        return clean_code

    def execute_test_suite(self) -> dict:
        """Runs the generated tests and parses results."""
        print("⚡ QA Agent: Executing test runner subprocess...")
        
        # Update the shared whiteboard status
        self.state.update_phase("TESTING", tasks=["Running test assertions"])
        
        try:
            # Run the test file using the local uv environment
            result = subprocess.run(
                ["uv", "run", "python", "-m", "unittest", str(self.test_file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Unittest outputs results to stderr by default
            output_log = result.stderr + "\n" + result.stdout
            
            if result.returncode == 0:
                print("🎉 QA Agent: ALL TESTS PASSED SUCCESSFULLY!")
                self.state.update_phase(
                    "COMPLETED", 
                    tasks=["Pipeline verified"], 
                    logs=f"All tests passed clean!\n{output_log}"
                )
                return {"status": "PASSED", "log": output_log}
            else:
                print("❌ QA Agent: TESTS FAILED. Initiating self-healing loop feedback...")
                self.state.update_phase(
                    "DEVELOPING", 
                    tasks=["Fixing test bugs flagged by QA"], 
                    logs=f"TEST FAILURE DETECTED:\n{output_log}"
                )
                return {"status": "FAILED", "log": output_log}
                
        except Exception as e:
            error_msg = f"QA Test execution crashed: {str(e)}"
            self.state.update_phase("TESTING", tasks=["Retry execution"], logs=error_msg)
            return {"status": "ERROR", "log": error_msg}
