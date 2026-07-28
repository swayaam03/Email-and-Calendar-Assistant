from langchain_openai import ChatOpenAI
from config.settings import settings

def get_openrouter_llm(temperature: float = 0.0, max_tokens: int = None) -> ChatOpenAI:
    """
    Returns a configured LangChain ChatOpenAI instance pointed at OpenRouter API.
    Works seamlessly with free model identifiers like:
      - meta-llama/llama-3.3-70b-instruct:free
      - google/gemma-2-9b-it:free
      - qwen/qwen-2.5-72b-instruct:free
    """
    token_limit = max_tokens or settings.MAX_RESPONSE_TOKENS

    return ChatOpenAI(
        model_name=settings.OPENROUTER_MODEL,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        temperature=temperature,
        max_tokens=token_limit,
        default_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "LangGraph-Email-Calendar-Assistant",
        }
    )
