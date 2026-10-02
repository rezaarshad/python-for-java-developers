"""Lesson 14 exercise: the notes app gets a brain.

Every function takes `client` as a parameter (dependency injection), so tests can pass a fake.
Always call through client.beta.messages.* with **LLM_OPTIONS (model + refusal fallback).

Test:  uv run pytest lessons/14_llm_claude/exercise -v      (no API key needed)
Try:   uv run python lessons/14_llm_claude/exercise/try_it.py (needs ANTHROPIC_API_KEY)
"""

import json
from collections.abc import Iterator

from pydantic import BaseModel, field_validator

MODEL = "claude-opus-5-5"
LLM_OPTIONS = {"model": MODEL, "betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}
PRICE_PER_MTOK = {"input": 4.00, "output": 20.00}     # Claude Opus 5.5, USD per million tokens

SUMMARY_SYSTEM = (
    "You summarize personal notes for a note-taking app. "
    "Reply with only the summary: at most {max_words} words, no preamble."
)


class RefusedError(Exception):
    """The model declined the request (stop_reason == "refusal")."""


# --- Helpers ---------------------------------------------------------------------------
def check_refusal(message) -> None:
    """Raise RefusedError if message.stop_reason == "refusal". Include the refusal category in
    the error message when message.stop_details is not None (message.stop_details.category)."""
    # TODO
    pass


def text_of(message) -> str:
    """Call check_refusal first, then join the .text of every content block whose .type == "text".
    (Responses can also contain "thinking" or "tool_use" blocks. Skip those.)"""
    # TODO
    pass


def cost_usd(message) -> float:
    """Price of one response from message.usage.input_tokens / .output_tokens and PRICE_PER_MTOK."""
    # TODO
    pass


# --- 1. Summarize -------------------------------------------------------------------------
def summarize(client, body: str, max_words: int = 30) -> str:
    """One request:
    - client.beta.messages.create(**LLM_OPTIONS, max_tokens=1024, output_config={"effort": "low"},
      system=SUMMARY_SYSTEM formatted with max_words, messages=[one user message with `body`])
    - return the stripped text."""
    # TODO
    pass


# --- 2. Structured output -------------------------------------------------------------------
class TagSuggestion(BaseModel):
    tags: list[str]
    reason: str

    @field_validator("tags")
    @classmethod
    def normalize(cls, tags: list[str]) -> list[str]:
        """lowercase + strip, drop empties, dedupe keeping order, keep at most 5."""
        # TODO
        pass


def suggest_tags(client, title: str, body: str, existing_tags: list[str]) -> TagSuggestion:
    """client.beta.messages.parse(**LLM_OPTIONS, max_tokens=1024, output_config={"effort": "low"},
    output_format=TagSuggestion, messages=[...]).
    The user message must contain the title, the body, and the existing tags (comma-separated) and
    ask Claude to prefer existing tags. Call check_refusal(response), then return response.parsed_output."""
    # TODO
    pass


# --- 3. Streaming --------------------------------------------------------------------------------
def stream_answer(client, question: str) -> Iterator[str]:
    """Generator: open `with client.beta.messages.stream(**LLM_OPTIONS, max_tokens=4096,
    messages=[...]) as stream:` and yield every chunk of stream.text_stream."""
    # TODO
    yield ""   # placeholder, replace


# --- 4. Chat with memory ---------------------------------------------------------------------------
class NoteChat:
    """A conversation about the user's notes. The API is stateless, so this class keeps the history."""

    def __init__(self, client, notes: list[dict]) -> None:
        """notes: [{"id": 1, "title": "...", "body": "..."}]. Build self.system ONCE:
        'Answer questions using these notes:\n' followed by one line per note: '[<id>] <title>: <body>'.
        self.history starts empty."""
        # TODO
        pass

    def ask(self, question: str) -> str:
        """Append the user message, call client.beta.messages.create(**LLM_OPTIONS, max_tokens=2048,
        system=self.system, messages=self.history), append {"role": "assistant", "content": response.content}
        (the content blocks, not just the text), and return text_of(response).
        If the call raises, the history must be left as it was before the call."""
        # TODO
        pass


# --- 5. Tool use: a hand-written agent loop -----------------------------------------------------------
SEARCH_TOOL = {
    "name": "search_notes",
    "description": "Search the user's notes. Returns a JSON list of {id, title, body} for notes whose "
                   "title or body contains ANY of the query words (case-insensitive).",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "Space-separated keywords"}},
        "required": ["query"],
        "additionalProperties": False,
    },
    "strict": True,
}


def search_notes(notes: list[dict], query: str) -> str:
    """The tool's implementation: JSON (json.dumps) list of matching notes, in their original order."""
    # TODO
    pass


def answer_with_tools(client, question: str, notes: list[dict], max_turns: int = 5) -> str:
    """The agent loop (lesson.md § 7):

        messages = [user question]
        repeat up to max_turns times:
            response = client.beta.messages.create(**LLM_OPTIONS, max_tokens=4096, tools=[SEARCH_TOOL], messages=messages)
            check_refusal(response)
            if response.stop_reason != "tool_use": return text_of(response)
            append {"role": "assistant", "content": response.content}
            for EVERY block with .type == "tool_use":
                name "search_notes" → content = search_notes(notes, block.input["query"])
                any other name → content = f"Unknown tool: {name}", with "is_error": True
                build {"type": "tool_result", "tool_use_id": block.id, "content": ...}
            append ONE user message whose content is the list of all tool_result dicts
        raise RuntimeError("too many tool turns") if it never finished
    """
    # TODO
    pass
