from typing import List, Dict, Any
from pydantic import BaseModel, Field

class HackathonState(BaseModel):
    """The global state shared across all nodes in our LangGraph."""
    input_query: str = Field(default="", description="The primary user input or hackathon challenge task.")
    sub_tasks: List[str] = Field(default_factory=list, description="The list of mapped sub-tasks to run in parallel.")
    mapped_results: Dict[str, str] = Field(default_factory=dict, description="Parallel processing responses from the LLM.")
    final_output: str = Field(default="", description="The final compiled solution after the reduce step.")
