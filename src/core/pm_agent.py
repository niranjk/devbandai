from __future__ import annotations

import re

from src.core.llm_client import LLMError, LocalQwenClient
from src.core.state import (
    DevBandState,
    FeatureSpec,
    PipelinePhase,
    ProjectStateManager,
    TaskSpec,
    log_entry,
)

AGENT_NAME = "PM_AGENT"


class ProductManagerAgent:
    """Parses raw requirements into a structured FeatureSpec via the LLM."""

    def __init__(self, state_manager: ProjectStateManager, llm_client: LocalQwenClient):
        self.state = state_manager
        self.llm = llm_client

    def process_new_requirement(self, raw_requirement: str) -> FeatureSpec | None:
        """Parse the requirement via the LLM and write the spec to the whiteboard."""
        print("📋 PM Agent: Analyzing raw requirement via LLM...")
        try:
            spec_output = self.llm.generate_response(
                system_prompt=self._system_prompt(),
                user_prompt=f"Analyze this requirement and break it down:\n{raw_requirement}",
            )

            feature_spec = self._parse_spec(spec_output)
            tasks = [
                f"Create {feature_spec.target_file}",
                "Ensure code handles edge cases",
                "Expose functional logic for QA test suite",
            ]
            logs = (
                f"### Feature Specification\n"
                f"TARGET FILE: {feature_spec.target_file}\n"
                f"EXPECTED BEHAVIOR: {feature_spec.expected_behavior}\n"
                f"UNIT TEST CASES: {', '.join(feature_spec.unit_test_cases)}\n"
                f"RAW SPEC:\n{feature_spec.raw_spec}\n"
            )
            self.state.update_phase("DEVELOPING", tasks=tasks, logs=logs)
            print(f"✅ PM Agent: Spec parsed — target file: {feature_spec.target_file}")
            return feature_spec

        except LLMError as exc:
            print(f"❌ PM Agent: LLM unreachable — {exc}")
            self.state.update_phase("FAILED", logs=f"PM_AGENT LLM FAILURE: {exc}")
            return None

    def _system_prompt(self) -> str:
        return (
            "You are an expert technical Product Manager Agent.\n"
            "Your job is to take a raw feature request and break it down into "
            "clean, actionable development tasks.\n"
            "You must output your analysis in an explicit format with three "
            "specific sections, each on its own line prefixed exactly:\n"
            "TARGET FILE: <filename>\n"
            "EXPECTED BEHAVIOR: <description>\n"
            "UNIT TEST CASES: <comma-separated list>\n"
            "Do not include any conversational filler. Be direct and technical."
        )

    @staticmethod
    def _parse_spec(raw_output: str) -> FeatureSpec:
        target_file = ""
        expected_behavior = ""
        test_cases: list[str] = []

        for line in raw_output.splitlines():
            line = line.strip()
            if line.upper().startswith("TARGET FILE:"):
                target_file = line.split(":", 1)[1].strip()
            elif line.upper().startswith("EXPECTED BEHAVIOR:"):
                expected_behavior = line.split(":", 1)[1].strip()
            elif line.upper().startswith("UNIT TEST CASES:"):
                raw_cases = line.split(":", 1)[1].strip()
                test_cases = [
                    c.strip() for c in raw_cases.split(",") if c.strip()
                ]

        if not target_file:
            m = re.search(r"(\w+\.py)", raw_output)
            if m:
                target_file = m.group(1)

        return FeatureSpec(
            target_file=target_file or "output_tool.py",
            expected_behavior=expected_behavior or raw_output[:200],
            unit_test_cases=test_cases,
            raw_spec=raw_output,
        )

    def __call__(self, state: DevBandState) -> dict:
        raw_requirement = state.get("raw_requirement", "")
        messages: list[str] = [log_entry(AGENT_NAME, f"Processing: {raw_requirement[:80]}...")]

        try:
            spec_output = self.llm.generate_response(
                system_prompt=self._system_prompt(),
                user_prompt=f"Analyze this requirement and break it down:\n{raw_requirement}",
            )

            feature_spec = self._parse_spec(spec_output)
            tasks = [
                TaskSpec(description=f"Create {feature_spec.target_file}"),
                TaskSpec(description="Ensure code handles edge cases"),
                TaskSpec(description="Expose functional logic for QA test suite"),
            ]

            messages.append(
                log_entry(AGENT_NAME, f"Spec parsed — target: {feature_spec.target_file}")
            )
            messages.append(
                log_entry(AGENT_NAME, f"Test cases identified: {len(feature_spec.unit_test_cases)}")
            )

            return {
                "phase": PipelinePhase.PLANNING,
                "feature_spec": feature_spec,
                "tasks": tasks,
                "messages": messages,
                "needs_human_review": True,
                "has_error": False,
            }

        except LLMError as exc:
            messages.append(log_entry(AGENT_NAME, f"LLM FAILURE: {exc}"))
            return {
                "phase": PipelinePhase.FAILED,
                "has_error": True,
                "error_trace": [f"{AGENT_NAME}: {exc}"],
                "messages": messages,
            }
        except Exception as exc:
            messages.append(log_entry(AGENT_NAME, f"UNEXPECTED FAILURE: {exc}"))
            return {
                "phase": PipelinePhase.FAILED,
                "has_error": True,
                "error_trace": [f"{AGENT_NAME}: {exc}"],
                "messages": messages,
            }
