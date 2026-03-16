import os
from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    current_file = Path(__file__).resolve()
    backend_dir = current_file.parents[1]
    workspace_dir = backend_dir.parent

    load_dotenv(backend_dir / ".env", override=False)
    load_dotenv(workspace_dir / ".env", override=False)


def ensure_langsmith_api_key() -> None:
    has_langsmith_key = bool(os.getenv("LANGSMITH_API_KEY"))
    has_langchain_key = bool(os.getenv("LANGCHAIN_API_KEY"))
    if has_langsmith_key or has_langchain_key:
        return

    raise RuntimeError(
        "LangSmith API key not found. Define LANGSMITH_API_KEY in .env (workspace root or backend/.env)."
    )
