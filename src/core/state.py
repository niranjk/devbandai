from __future__ import annotations

import operator
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, TypedDict

from pydantic import BaseModel, Field


class PipelinePhase(str, Enum):
    INITIALIZATION = "INITIALIZATION"
    PLANNING = "PLANNING"
    DEVELOPING = "DEVELOPING"
    TESTING = "TESTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskSpec(BaseModel):
    description: str
    completed: bool = False


class FeatureSpec(BaseModel):
    target_file: str = ""
    expected_behavior: str = ""
    unit_test_cases: list[str] = Field(default_factory=list)
    raw_spec: str = ""


class TestResult(BaseModel):
    status: str = "PENDING"
    log: str = ""
    return_code: int = -1


class DevBandState(TypedDict, total=False):
    raw_requirement: str
    phase: PipelinePhase
    feature_spec: FeatureSpec
    tasks: list[TaskSpec]
    generated_code: str
    test_code: str
    test_result: TestResult
    messages: Annotated[list[str], operator.add]
    error_trace: Annotated[list[str], operator.add]
    loop_count: int
    max_loops: int
    needs_human_review: bool
    human_approved: bool
    qa_passed: bool
    dev_succeeded: bool
    has_error: bool


def log_entry(agent: str, message: str) -> str:
    ts = datetime.now().strftime("%H:%M:%S")
    return f"[{ts}] [{agent}] {message}"


class ProjectStateManager:
    """Disk-persistence layer that mirrors pipeline state to .scratchpad.md.

    Acts as the shared "whiteboard" every agent reads from and writes to.
    """

    def __init__(self, workspace_dir: str = "."):
        self.workspace = Path(workspace_dir).resolve()
        self.scratchpad_path = self.workspace / ".scratchpad.md"
        self.init_scratchpad()

    def init_scratchpad(self) -> None:
        if not self.scratchpad_path.exists():
            content = (
                "# DEVBAND SYSTEM SCRATCHPAD\n\n"
                "## Current Pipeline State\n- Active Phase: INITIALIZATION\n"
                "- Last Updated: Never\n\n"
                "## Active Task List\n- [ ] Initialize system loop\n\n"
                "## Execution Logs & Test Metrics\n- No runs yet.\n"
            )
            self.scratchpad_path.write_text(content, encoding="utf-8")

    def update_phase(
        self,
        phase: PipelinePhase | str,
        tasks: list[str] | None = None,
        logs: str = "",
    ) -> None:
        phase_str = (
            phase.value if isinstance(phase, PipelinePhase) else str(phase)
        )
        task_str = (
            "\n".join(f"- [ ] {t}" for t in tasks)
            if tasks
            else "- No pending tasks."
        )
        content = (
            f"# DEVBAND SYSTEM SCRATCHPAD\n\n"
            f"## Current Pipeline State\n- Active Phase: {phase_str.upper()}\n"
            f"- Last Updated: {datetime.now().isoformat()}\n\n"
            f"## Active Task List\n{task_str}\n\n"
            f"## Execution Logs & Test Metrics\n{logs or '- Clean slate.'}\n"
        )
        with open(self.scratchpad_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
