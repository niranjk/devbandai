import time
from src.core.state import ProjectStateManager
from src.core.llm_client import LocalQwenClient
from src.core.pm_agent import ProductManagerAgent
from src.core.developer_agent import DeveloperAgent
from src.core.qa_agent import QAGerAgent

class DevBandOrchestrator:
    def __init__(self):
        self.state_manager = ProjectStateManager()
        self.llm_client = LocalQwenClient()
        
        # Instantiate our 3 Band agents
        self.pm_agent = ProductManagerAgent(self.state_manager, self.llm_client)
        self.dev_agent = DeveloperAgent(self.state_manager)
        self.qa_agent = QAGerAgent(self.state_manager, self.llm_client)
        
        self.max_loops = 3  # Prevent infinite execution loops locally

    def get_current_phase(self) -> str:
        """Parses the current phase directly from the whiteboard."""
        if not self.state_manager.scratchpad_path.exists():
            return "INITIALIZATION"
        
        lines = self.state_manager.scratchpad_path.read_text().splitlines()
        for line in lines:
            if "- Active Phase:" in line:
                return line.split("Active Phase:")[-1].strip().upper()
        return "INITIALIZATION"

    def run_pipeline(self, raw_requirement: str):
        """The core state router loop coordinating the multi-agent system."""
        print("\n🏁 ===============================================")
        print("🚀 DEVBAND MULTI-AGENT STATE MACHINE RUNNER ACTIVE")
        print("===================================================\n")
        
        # Step A: Kick off with the Product Manager Agent
        self.pm_agent.process_new_requirement(raw_requirement)
        
        loop_counter = 0
        while loop_counter < self.max_loops:
            current_phase = self.get_current_phase()
            print(f"\n[🔄 Loop Counter: {loop_counter+1}/{self.max_loops}] - Current State Engine Node: {current_phase}")
            
            if current_phase == "DEVELOPING":
                print("➡️ Routing token to: DEVELOPER AGENT")
                dev_result = self.dev_agent.execute_code_generation()
                if dev_result["status"] == "FAILED":
                    print("⚠️ Dev Agent ran into a compile barrier. Retrying script optimization...")
            
            elif current_phase == "TESTING":
                print("➡️ Routing token to: QUALITY ASSURANCE AGENT")
                # 1. Synthesize the unit test scripts
                self.qa_agent.generate_and_save_test_suite()
                # 2. Run test assertions
                qa_result = self.qa_agent.execute_test_suite()
                
                if qa_result["status"] == "PASSED":
                    print("\n🏆 SUCCESS: Code matches requirements perfectly. Halting state machine.")
                    break
                else:
                    print("⚠️ Self-Healing Loop Triggered: Failure parameters logged to whiteboard.")
            
            elif current_phase == "COMPLETED":
                print("\n🎉 Pipeline Complete! Verified code artifact generated.")
                break

            elif current_phase == "FAILED":
                print("\n🚨 Pipeline halted: a fatal agent error was reported. Check the whiteboard logs.")
                break

            else:
                print(f"⚠️ Unhandled state or parsing latency: {current_phase}. Defaulting to Dev iteration.")
                self.state_manager.update_phase("DEVELOPING")
                
            loop_counter += 1
            time.sleep(2)  # Short pause to prevent disk locking logs on your M1 Mac
            
        if loop_counter >= self.max_loops:
            print("\n🚨 PIPELINE TIMEOUT: Maximum fallback iterations reached without a green clean build.")
