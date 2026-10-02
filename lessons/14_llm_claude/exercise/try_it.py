"""Try your llm_notes functions against the real API (needs ANTHROPIC_API_KEY; costs a few cents).

Run: uv run python lessons/14_llm_claude/exercise/try_it.py
"""

import os
import sys

import anthropic

from llm_notes import NoteChat, answer_with_tools, stream_answer, suggest_tags, summarize

NOTES = [
    {"id": 1, "title": "RAG", "body": "Retrieval augmented generation: find relevant notes with embeddings, "
                                       "then pass them to Claude as context so answers are grounded in my notes."},
    {"id": 2, "title": "pytest", "body": "Fixtures replace @BeforeEach; parametrize replaces @ParameterizedTest."},
    {"id": 3, "title": "Groceries", "body": "oat milk, coffee beans, bananas"},
]

if not os.environ.get("ANTHROPIC_API_KEY"):
    sys.exit("Set ANTHROPIC_API_KEY first.")

client = anthropic.Anthropic()
print("summary:", summarize(client, NOTES[0]["body"], max_words=15))
print("tags:", suggest_tags(client, NOTES[0]["title"], NOTES[0]["body"], ["ai", "python", "personal"]))
print("stream: ", end="")
for chunk in stream_answer(client, "In one sentence: why do Java devs like Python for AI?"):
    print(chunk, end="", flush=True)
print()
chat = NoteChat(client, NOTES)
print("chat 1:", chat.ask("What do I need to buy?"))
print("chat 2:", chat.ask("Which of those is a drink?"))
print("agent:", answer_with_tools(client, "What did I write about testing? Search my notes.", NOTES))
