"""Lesson 14 demo: the Claude API with the anthropic SDK.

Needs ANTHROPIC_API_KEY. Makes ~8 small requests (a few cents in total).
Run: uv run python lessons/14_llm_claude/claude_demo.py
"""

import asyncio
import json
import os
import sys

import anthropic
from anthropic import beta_tool
from pydantic import BaseModel

MODEL = "claude-opus-5-5"
# Opt in to server-side refusal fallback on every call (see lesson.md § 3)
OPTIONS = {"model": MODEL, "betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}


def text_of(message) -> str:
    if message.stop_reason == "refusal":
        return f"[refused: {message.stop_details.category if message.stop_details else 'unknown'}]"
    return "".join(b.text for b in message.content if b.type == "text")


def header(title: str) -> None:
    print(f"\n{'=' * 10} {title} {'=' * 10}")


def basic(client: anthropic.Anthropic) -> None:
    header("basic request + system prompt")
    message = client.beta.messages.create(
        **OPTIONS,
        max_tokens=1024,
        output_config={"effort": "low"},       # a simple task → low effort is faster and cheaper
        system="You explain things to senior Java developers. Be brief.",
        messages=[{"role": "user", "content": "What's the Python equivalent of a Java record?"}],
    )
    print(text_of(message))
    print(f"[stop_reason={message.stop_reason}, in={message.usage.input_tokens}, out={message.usage.output_tokens}]")


def multi_turn(client: anthropic.Anthropic) -> None:
    header("multi-turn (you send the history)")
    history: list[dict] = [{"role": "user", "content": "My favourite language is Java. Remember that."}]
    first = client.beta.messages.create(**OPTIONS, max_tokens=512, output_config={"effort": "low"}, messages=history)
    history.append({"role": "assistant", "content": first.content})
    history.append({"role": "user", "content": "Which language did I say? One word."})
    second = client.beta.messages.create(**OPTIONS, max_tokens=512, output_config={"effort": "low"}, messages=history)
    print(text_of(second))


def streaming(client: anthropic.Anthropic) -> None:
    header("streaming")
    with client.beta.messages.stream(
        **OPTIONS,
        max_tokens=2048,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": "Write a haiku about Python's indentation."}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        final = stream.get_final_message()
    print(f"\n[{final.usage.output_tokens} output tokens]")


class NoteMeta(BaseModel):
    title: str
    tags: list[str]
    priority: str


def structured(client: anthropic.Anthropic) -> None:
    header("structured output (pydantic)")
    response = client.beta.messages.parse(
        **OPTIONS,
        max_tokens=1024,
        output_config={"effort": "low"},
        output_format=NoteMeta,
        messages=[{"role": "user", "content": "Make note metadata for: 'Ship the RAG demo by Friday, "
                                              "uses embeddings + Claude'. priority is low, medium or high."}],
    )
    meta = response.parsed_output          # a validated NoteMeta instance
    print(repr(meta))


NOTES = {
    1: "RAG = retrieve relevant notes, then put them in the prompt.",
    2: "pytest fixtures replace @BeforeEach.",
    3: "Groceries: oat milk, coffee.",
}


@beta_tool
def search_notes(query: str) -> str:
    """Search the user's notes by keyword.

    Args:
        query: One or two keywords to look for.
    """
    hits = {i: t for i, t in NOTES.items() if any(w.lower() in t.lower() for w in query.split())}
    print(f"   🔧 search_notes({query!r}) → {list(hits)}")
    return json.dumps(hits)


def tools(client: anthropic.Anthropic) -> None:
    header("tool use with the SDK tool runner")
    runner = client.beta.messages.tool_runner(
        **OPTIONS,
        max_tokens=2048,
        tools=[search_notes],
        messages=[{"role": "user", "content": "What did I write about testing? Use search_notes."}],
    )
    final = None
    for message in runner:                 # each iteration = one model turn; tools run automatically
        final = message
    print(text_of(final))


async def concurrent() -> None:
    header("AsyncAnthropic + gather")
    async with anthropic.AsyncAnthropic() as client:
        words = ["generator", "decorator", "dataclass"]
        replies = await asyncio.gather(*(
            client.beta.messages.create(**OPTIONS, max_tokens=256, output_config={"effort": "low"},
                                        messages=[{"role": "user", "content": f"Define Python's {w} in 10 words."}])
            for w in words
        ))
        for w, r in zip(words, replies):
            print(f"{w}: {text_of(r)}")


def errors(client: anthropic.Anthropic) -> None:
    header("error handling")
    try:
        client.messages.create(model="claude-does-not-exist", max_tokens=10,
                               messages=[{"role": "user", "content": "hi"}])
    except anthropic.NotFoundError as e:
        print("NotFoundError:", e.status_code)
    except anthropic.RateLimitError:
        print("rate limited, back off and retry")
    except anthropic.APIStatusError as e:
        print("API error", e.status_code, e.message)
    except anthropic.APIConnectionError:
        print("network problem")


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY first (https://console.anthropic.com). The exercise tests don't need one.")
    client = anthropic.Anthropic()
    basic(client)
    multi_turn(client)
    streaming(client)
    structured(client)
    tools(client)
    asyncio.run(concurrent())
    errors(client)


if __name__ == "__main__":
    main()
