"""
LLM abstraction layer.

To switch to Ollama:
  1. Set LLM_BACKEND=ollama in .env
  2. pip install openai
  3. Ensure Ollama is running: ollama serve
  4. Pull a model: ollama pull llama3.1:8b

All app code calls stream_response() or get_response() — nothing else changes.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BACKEND       = os.getenv("LLM_BACKEND", "anthropic")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
OLLAMA_MODEL  = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
ACTIVE_MODEL  = OLLAMA_MODEL if BACKEND == "ollama" else ANTHROPIC_MODEL


def _anthropic_stream(messages: list[dict], system: str):
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    with client.messages.stream(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def _ollama_stream(messages: list[dict], system: str):
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "Ollama backend requires openai package. Run: pip install openai"
        )
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    full_messages = ([{"role": "system", "content": system}] if system else []) + messages
    stream = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=full_messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def stream_response(messages: list[dict], system: str = ""):
    """Yield text chunks from the configured LLM backend."""
    if BACKEND == "ollama":
        yield from _ollama_stream(messages, system)
    else:
        yield from _anthropic_stream(messages, system)


def get_response(messages: list[dict], system: str = "") -> str:
    """Return the full LLM response as a single string."""
    return "".join(stream_response(messages, system))
