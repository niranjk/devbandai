from langgraph.graph import StateGraph, START, END
from src.core.state import HackathonState

def planner_node(state):
    """Node 1 (Map Init): Breaks down the main query into 2 distinct sub-tasks."""
    # Lazy instantiation breaks the circular import freeze
    from src.core.llm_client import HackathonLLM
    llm = HackathonLLM()
    
    prompt = f"Break down this hackathon goal into exactly two specific technical requirements, separated by a newline: {state.input_query}"
    
    response = llm.generate(
        prompt=prompt, 
        system_instruction="You are a system architect. Respond with exactly two short bullet-points, no intro."
    )
    
    tasks = [line.strip("- ") for line in response.strip().split("\n") if line.strip()]
    return {"sub_tasks": tasks}

def worker_node(state):
    """Node 2 (Map Execution): Simulates or loops through the tasks."""
    from src.core.llm_client import HackathonLLM
    llm = HackathonLLM()
    
    results = {}
    for task in state.sub_tasks:
        prompt = f"Solve this specific requirement efficiently: {task}"
        response = llm.generate(
            prompt=prompt,
            system_instruction="Provide a brief, highly tactical engineering answer."
        )
        results[task] = response
    return {"mapped_results": results}

def compiler_node(state):
    """Node 3 (Reduce): Consolidates all the parallel answers into a final response."""
    from src.core.llm_client import HackathonLLM
    llm = HackathonLLM()
    
    context = ""
    for task, result in state.mapped_results.items():
        context += f"Requirement: {task}\nSolution: {result}\n\n"
        
    prompt = f"Based on the following sub-solutions, compile a comprehensive master implementation blueprint:\n\n{context}"
    final_response = llm.generate(
        prompt=prompt,
        system_instruction="You are a master engineer. Combine these components cleanly."
    )
    return {"final_output": final_response}

# Assemble the Blueprint Graph Layout
workflow = StateGraph(HackathonState)

# Add our processing units
workflow.add_node("planner", planner_node)
workflow.add_node("worker", worker_node)
workflow.add_node("compiler", compiler_node)

# Set the execution path mappings
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "worker")
workflow.add_edge("worker", "compiler")
workflow.add_edge("compiler", END)

# Compile graph into an executable runtime engine mapping
hackathon_engine = workflow.compile()
