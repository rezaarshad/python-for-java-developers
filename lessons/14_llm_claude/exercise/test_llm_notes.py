"""Provided tests with a FAKE Anthropic client. No API key, no network, no cost.

Run: uv run pytest lessons/14_llm_claude/exercise -v
"""

import json
from contextlib import contextmanager
from types import SimpleNamespace as NS

import pytest

from llm_notes import (
    LLM_OPTIONS,
    SEARCH_TOOL,
    NoteChat,
    RefusedError,
    TagSuggestion,
    answer_with_tools,
    cost_usd,
    search_notes,
    stream_answer,
    suggest_tags,
    summarize,
    text_of,
)


# --- Fakes that mimic the SDK's response shapes -------------------------------------------------
def text(t):
    return NS(type="text", text=t)


def tool_use(id, name, **input):
    return NS(type="tool_use", id=id, name=name, input=input)


def message(*blocks, stop_reason="end_turn", stop_details=None, input_tokens=10, output_tokens=5):
    return NS(content=list(blocks), stop_reason=stop_reason, stop_details=stop_details,
              usage=NS(input_tokens=input_tokens, output_tokens=output_tokens))


class FakeMessages:
    def __init__(self, responses=(), parsed=None, chunks=()):
        self.responses = list(responses)     # returned by create(), in order
        self.parsed = parsed
        self.chunks = list(chunks)
        self.calls = []                      # kwargs of every call, for assertions

    def create(self, **kwargs):
        # snapshot the messages list: the code under test may keep mutating it after the call
        self.calls.append({**kwargs, "messages": list(kwargs.get("messages", []))})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return NS(parsed_output=self.parsed, stop_reason="end_turn", stop_details=None, content=[])

    @contextmanager
    def stream(self, **kwargs):
        self.calls.append(kwargs)
        yield NS(text_stream=iter(self.chunks))


def fake_client(**kwargs):
    messages = FakeMessages(**kwargs)
    return NS(beta=NS(messages=messages)), messages


def assert_uses_options(call):
    for key, value in LLM_OPTIONS.items():
        assert call[key] == value, f"pass **LLM_OPTIONS (missing/wrong {key!r})"


NOTES = [
    {"id": 1, "title": "RAG", "body": "Retrieve notes, then prompt Claude"},
    {"id": 2, "title": "pytest", "body": "Fixtures replace BeforeEach"},
    {"id": 3, "title": "Groceries", "body": "oat milk and coffee"},
]


# --- Helpers ---------------------------------------------------------------------------------------
def test_text_of_joins_text_blocks_only():
    m = message(NS(type="thinking", thinking=""), text("Hello "), tool_use("t1", "x"), text("world"))
    assert text_of(m) == "Hello world"


def test_text_of_raises_on_refusal_with_category():
    m = message(stop_reason="refusal", stop_details=NS(category="cyber", explanation="..."))
    with pytest.raises(RefusedError, match="cyber"):
        text_of(m)


def test_text_of_refusal_without_details():
    with pytest.raises(RefusedError):
        text_of(message(stop_reason="refusal"))


def test_cost_usd():
    m = message(input_tokens=1_000_000, output_tokens=500_000)
    assert cost_usd(m) == pytest.approx(4.0 + 10.0)


# --- Summarize --------------------------------------------------------------------------------------
def test_summarize_request_and_result():
    client, msgs = fake_client(responses=[message(text("  A short summary.  "))])
    assert summarize(client, "long note body", max_words=12) == "A short summary."
    call = msgs.calls[0]
    assert_uses_options(call)
    assert call["output_config"] == {"effort": "low"}
    assert "12 words" in call["system"]
    assert call["messages"] == [{"role": "user", "content": "long note body"}]
    assert call["max_tokens"] == 1024


# --- Structured output ----------------------------------------------------------------------------------
def test_tag_suggestion_normalizes():
    s = TagSuggestion(tags=[" AI ", "llm", "ai", "", "Python", "rag", "data", "extra"], reason="r")
    assert s.tags == ["ai", "llm", "python", "rag", "data"]


def test_suggest_tags_prompt_and_parse():
    suggestion = TagSuggestion(tags=["ai"], reason="it's about AI")
    client, msgs = fake_client(parsed=suggestion)
    assert suggest_tags(client, "RAG demo", "embeddings and Claude", ["ai", "python"]) is suggestion
    call = msgs.calls[0]
    assert_uses_options(call)
    assert call["output_format"] is TagSuggestion
    prompt = json.dumps(call["messages"])
    for expected in ["RAG demo", "embeddings and Claude", "ai, python"]:
        assert expected in prompt


# --- Streaming ------------------------------------------------------------------------------------------
def test_stream_answer_yields_chunks():
    client, msgs = fake_client(chunks=["Hel", "lo", "!"])
    gen = stream_answer(client, "hi?")
    assert iter(gen) is gen, "stream_answer must be a generator"
    assert list(gen) == ["Hel", "lo", "!"]
    assert_uses_options(msgs.calls[0])
    assert msgs.calls[0]["messages"] == [{"role": "user", "content": "hi?"}]


# --- Chat ------------------------------------------------------------------------------------------------
def test_chat_builds_system_prompt_once():
    client, msgs = fake_client(responses=[message(text("a")), message(text("b"))])
    chat = NoteChat(client, NOTES)
    assert chat.system.startswith("Answer questions using these notes:\n")
    assert "[2] pytest: Fixtures replace BeforeEach" in chat.system
    chat.ask("q1")
    chat.ask("q2")
    assert msgs.calls[0]["system"] == msgs.calls[1]["system"] == chat.system


def test_chat_sends_full_history():
    first = message(text("Answer one"))
    client, msgs = fake_client(responses=[first, message(text("Answer two"))])
    chat = NoteChat(client, NOTES)
    assert chat.ask("What is RAG?") == "Answer one"
    assert chat.ask("And pytest?") == "Answer two"
    second_call_messages = msgs.calls[1]["messages"]
    assert second_call_messages == [
        {"role": "user", "content": "What is RAG?"},
        {"role": "assistant", "content": first.content},
        {"role": "user", "content": "And pytest?"},
    ]
    assert len(chat.history) == 4


def test_chat_history_unchanged_when_call_fails():
    client, _ = fake_client(responses=[message(text("ok")), ConnectionError("down")])
    chat = NoteChat(client, NOTES)
    chat.ask("first")
    with pytest.raises(ConnectionError):
        chat.ask("second")
    assert len(chat.history) == 2, "a failed call must not leave a dangling user message"


# --- Tools --------------------------------------------------------------------------------------------------
def test_search_notes():
    assert [n["id"] for n in json.loads(search_notes(NOTES, "claude COFFEE"))] == [1, 3]
    assert json.loads(search_notes(NOTES, "kotlin")) == []


def test_answer_without_tools():
    client, msgs = fake_client(responses=[message(text("Direct answer"))])
    assert answer_with_tools(client, "hi", NOTES) == "Direct answer"
    assert msgs.calls[0]["tools"] == [SEARCH_TOOL]
    assert_uses_options(msgs.calls[0])


def test_answer_with_one_tool_round_trip():
    turn1 = message(text("Let me search."), tool_use("tu_1", "search_notes", query="pytest"), stop_reason="tool_use")
    client, msgs = fake_client(responses=[turn1, message(text("Fixtures replace BeforeEach."))])
    assert answer_with_tools(client, "What about testing?", NOTES) == "Fixtures replace BeforeEach."
    second = msgs.calls[1]["messages"]
    assert second[0] == {"role": "user", "content": "What about testing?"}
    assert second[1] == {"role": "assistant", "content": turn1.content}
    assert second[2]["role"] == "user"
    [result] = second[2]["content"]
    assert result["type"] == "tool_result" and result["tool_use_id"] == "tu_1"
    assert [n["id"] for n in json.loads(result["content"])] == [2]
    assert not result.get("is_error")


def test_parallel_tool_calls_go_back_in_one_message():
    turn1 = message(tool_use("a", "search_notes", query="rag"), tool_use("b", "delete_everything"),
                    stop_reason="tool_use")
    client, msgs = fake_client(responses=[turn1, message(text("done"))])
    answer_with_tools(client, "q", NOTES)
    results = msgs.calls[1]["messages"][2]["content"]
    assert [r["tool_use_id"] for r in results] == ["a", "b"]
    assert results[1]["is_error"] is True and "Unknown tool: delete_everything" in results[1]["content"]


def test_tool_loop_is_capped():
    looping = [message(tool_use(f"t{i}", "search_notes", query="x"), stop_reason="tool_use") for i in range(10)]
    client, msgs = fake_client(responses=looping)
    with pytest.raises(RuntimeError):
        answer_with_tools(client, "q", NOTES, max_turns=3)
    assert len(msgs.calls) == 3


def test_tool_loop_refusal():
    client, _ = fake_client(responses=[message(stop_reason="refusal")])
    with pytest.raises(RefusedError):
        answer_with_tools(client, "q", NOTES)
