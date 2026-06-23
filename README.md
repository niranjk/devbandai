# DevBand AI

> Autonomous Multi-Agent Scrum Suite — an AI-driven software factory that turns a raw feature request into verified, tested code artifacts with zero manual coding.

Built for the **Band of Agents Hackathon**.

---

## Purpose

Software delivery is slow because it stitches together manual hand-offs: a product
manager writes requirements, a developer translates them into code, and a QA engineer
writes and runs tests to prove the code works. Each hand-off is slow, error-prone, and
blocks the next stage.

**DevBand AI solves this by replacing the human hand-offs with a self-organizing band of
AI agents.** You give it a single natural-language feature requirement and it autonomously:

1. **Plans** — breaks the requirement into a structured feature spec (target file,
   expected behavior, and unit-test cases).
2. **Develops** — generates the actual source code using an AI coding assistant.
3. **Tests** — synthesizes a `unittest` suite, executes it, and parses the results.
4. **Self-heals** — when tests fail, it feeds the failure log back to the developer
   agent and retries, looping until the code passes (or a max-iteration cap is hit).

The result is a verified, production-ready code artifact produced end-to-end by agents,
with a live dashboard for full observability of what each agent is doing.

---

## How It Works

DevBand AI is a **state-machine orchestrator** that routes a shared "whiteboard"
(the `.scratchpad.md` file) between three specialized agents:

```
INITIALIZATION -> PLANNING -> DEVELOPING -> TESTING --(pass)--> COMPLETED
                                  ^              |
                                  |---(fail)-----+   (self-healing loop)
```

| Agent | File | Responsibility |
|-------|------|----------------|
| **Product Manager Agent** | `src/core/pm_agent.py` | Parses the raw requirement via the LLM into a structured `FeatureSpec` (target file, expected behavior, unit-test cases). |
| **Developer Agent** | `src/core/developer_agent.py` | Reads the spec from the whiteboard and invokes [Aider](https://aider.chat) in headless mode to generate the code file. |
| **QA Agent** | `src/core/qa_agent.py` | Generates a `unittest` suite from the spec, runs it via subprocess, and reports pass/fail back to the orchestrator. |

The orchestrator (`src/core/graph.py`) reads the active phase from the whiteboard and
dispatches to the correct agent, looping up to a configurable number of iterations so a
failed test run automatically triggers another development pass.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Language | **Python 3.11.15** | Pinned via `.python-version` |
| Package manager | **uv** | Fast Python package/runner used throughout |
| Agent orchestration | **LangGraph** | State-machine framework for multi-agent workflows |
| Data validation | **Pydantic** | Typed state models (`FeatureSpec`, `TaskSpec`, `TestResult`) |
| HTTP client | **httpx** | Talks to the local LLM's OpenAI-compatible API |
| Retry / resilience | **tenacity** | Exponential backoff on LLM failures |
| Local LLM runtime | **Ollama** | Serves the model at `http://localhost:11434` |
| LLM model | **Qwen 2.5 Coder** | Default coding model (`qwen2.5-coder`) |
| AI code generation | **Aider** | Headless CLI pair-programmer used by the Developer Agent |
| Dashboard UI | **Streamlit** | Live observability dashboard for the agent pipeline |
| Environment config | **python-dotenv** | Loads `.env` variables |
| Remote inference (optional) | **Hugging Face Hub** / OpenAI / Gemini | Switchable via `LLM_PROVIDER` |
| Testing framework | **Python `unittest`** | Used by the QA Agent to verify generated code |

---

## Project Structure

```
devbandai/
├── main.py                      # CLI entry point — runs the full orchestrator pipeline
├── src/
│   ├── app.py                   # Alternative pipeline runner (LangGraph invoke)
│   ├── config.py                # Centralized env/config loader
│   ├── core/
│   │   ├── graph.py             # DevBandOrchestrator — the state-machine router
│   │   ├── state.py             # Pipeline phases, typed state, scratchpad logger
│   │   ├── llm_client.py        # OpenAI-compatible client for local Ollama/Qwen
│   │   ├── pm_agent.py          # Product Manager Agent
│   │   ├── developer_agent.py   # Developer Agent (Aider)
│   │   └── qa_agent.py          # QA Agent (unittest generation + execution)
│   └── ui/
│       └── app_ui.py            # Streamlit live dashboard
├── pyproject.toml               # Project metadata + dependencies
├── uv.lock                      # Locked dependency graph
├── .env.example                 # Template for environment variables
└── .scratchpad.md               # Shared "whiteboard" state file (generated at runtime)
```

---

## Prerequisites

- **Python 3.11.15** (managed automatically by `uv`)
- **[uv](https://docs.astral.sh/uv/)** — install with:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **[Ollama](https://ollama.com/)** — to serve the local Qwen model
- **[Aider](https://aider.chat/)** — the Developer Agent shells out to `aider`

---

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd devbandai
   ```

2. **Install Python dependencies with uv**
   ```bash
   uv sync
   ```
   This creates the virtual environment and installs everything from `uv.lock`.

3. **Pull the local LLM model via Ollama**
   ```bash
   ollama pull qwen2.5-coder
   ```

4. **Start the Ollama server** (keep it running in a separate terminal)
   ```bash
   ollama serve
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and fill in the values as needed:
   ```env
   # Choose: huggingface | openai | gemini
   LLM_PROVIDER=huggingface

   # API Keys
   HF_TOKEN=
   OPENAI_API_KEY=
   GEMINI_API_KEY=

   # Model Customization
   HF_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
   OPENAI_MODEL=gpt-4o-mini
   ```

---

## Running the App

### Option A — Run the full pipeline from the CLI

```bash
uv run python main.py
```

This fires the orchestrator with the built-in demo requirement (a Fibonacci tool) and
walks through the Plan -> Develop -> Test -> self-heal loop, writing the generated code
and test suite to the project root.

### Option B — Launch the live Streamlit dashboard

```bash
uv run streamlit run src/ui/app_ui.py
```

The dashboard shows real-time agent status, the active sprint backlog, execution logs
(parsed from `.scratchpad.md`), and a live view of the generated code file.

### Option C — Run the pipeline programmatically

```bash
uv run python -m src.app "your feature requirement here"
```

---

## Runtime Artifacts

While running, DevBand AI creates/updates these files in the project root:

- `.scratchpad.md` — the shared whiteboard tracking the active phase, task list, and logs.
- `<target_file>.py` — the generated code artifact (e.g. `fibonacci_tool.py`).
- `test_target_output.py` — the QA-generated `unittest` suite.

---

## License

See [LICENSE](LICENSE).
