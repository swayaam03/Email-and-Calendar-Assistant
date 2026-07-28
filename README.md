# AI Email & Calendar Assistant using LangGraph

An autonomous, token-efficient AI Executive Assistant built with **LangGraph**, **LangChain**, **OpenRouter API** (free LLM models), and **FastAPI**.

## Features

- **Autonomous Agentic Workflow**: Reasons, plans, and executes email & calendar management tasks using LangGraph `StateGraph`.
- **Zero External API Setup**: Uses an in-memory / SQLite-backed local Email & Calendar service engine. No Google Cloud OAuth required!
- **OpenRouter Free Model Tier**: Works seamlessly with OpenRouter free models like `meta-llama/llama-3.3-70b-instruct:free`, `google/gemma-2-9b-it:free`, and `qwen/qwen-2.5-72b-instruct`.
- **Token Efficiency**: Compact prompt designs, hard token limits, and snippet-level context truncation keep token usage minimal.
- **Human-in-the-Loop (HITL)**: Requires human review before sending emails or creating calendar events.

## Directory Structure

```
├── config/             # Settings, environment variables, intent constants
├── llm/                # OpenRouter ChatOpenAI provider wrapper
├── services/           # Local Email & Calendar database services
├── tools/              # LangChain tools (email, calendar, reminders, utils)
├── state/              # AgentState TypedDict definition
├── prompts/            # Token-optimized LLM prompts
├── agents/             # Intent classifier & specialized agents
├── graph/              # LangGraph StateGraph, conditional edges, HITL nodes
├── api/                # FastAPI application & REST endpoints
└── tests/              # Automated tests
```

## Quickstart

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   Copy `.env.example` to `.env` and fill in your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_actual_openrouter_api_key
   ```

3. **Run Tests**:
   ```bash
   pytest
   ```
