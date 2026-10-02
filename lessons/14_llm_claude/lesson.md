# Lesson 14: Building with LLMs: the Claude API

Everything so far (functions, classes, pydantic, httpx, async, testing) comes together here. The
`anthropic` SDK is a typed pydantic + HTTP client around one endpoint: `POST /v1/messages`.

## 1. Setup

```bash
uv add anthropic
export ANTHROPIC_API_KEY="sk-ant-..."     # from console.anthropic.com. Never commit it!
```

`anthropic.Anthropic()` reads the key from the environment. Keep secrets out of code; in real
projects, load them from env vars or a secrets manager (`pydantic-settings` reads `.env` files).

**Models** (as of this lesson): `claude-opus-5-5` (the default: most capable for everyday work),
`claude-sonnet-5-5` (faster and cheaper), `claude-haiku-4-5` (cheapest, for simple high-volume tasks).
Use the exact IDs. Prices are per million tokens (a token is ~¾ of a word): Opus 5.5 costs $4 input / $20 output.

## 2. Your first request

```python
import anthropic

client = anthropic.Anthropic()            # create once, reuse (like an HttpClient)

message = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,                      # hard cap on the response length
    system="You are a concise assistant for a note-taking app.",   # role, rules, context
    messages=[{"role": "user", "content": "Explain RAG in two sentences."}],
)

for block in message.content:             # a list of content blocks: text, thinking, tool_use...
    if block.type == "text":
        print(block.text)

message.stop_reason        # "end_turn" | "max_tokens" | "tool_use" | "refusal" | ...
message.usage              # input_tokens, output_tokens → this is what you pay for
```

Thinking: Claude Opus 5.5 always reasons internally before answering, and its **effort**
setting controls how much: `output_config={"effort": "low" | "medium" | "high" | "xhigh" | "max"}`.
The default is `medium`. Use `low` for simple tasks like summaries and tagging, and `high` or above for hard reasoning.

## 3. Refusals and fallbacks

Safety classifiers occasionally decline a request (`stop_reason == "refusal"`, still HTTP 200).
**Always check `stop_reason` before reading `content`.** On the Claude API you can opt in to an automatic
retry on another model, server-side, in the same call:

```python
message = client.beta.messages.create(           # the beta namespace accepts betas/fallbacks
    model="claude-opus-5-5",
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",                          # Anthropic picks the fallback model per refusal category
    max_tokens=1024,
    messages=[...],
)
```

This course enables it on every call (see `LLM_OPTIONS` in the exercise).

## 4. Conversations are stateless

The API has no memory: **you send the whole history each time**.

```python
history = [{"role": "user", "content": "My name is Reza."}]
reply = client.messages.create(model=..., max_tokens=1024, messages=history)
history.append({"role": "assistant", "content": reply.content})   # append the content blocks as-is
history.append({"role": "user", "content": "What's my name?"})
```

## 5. Streaming

Tokens arrive as they're generated, which makes for better UX and avoids timeouts on long outputs:

```python
with client.messages.stream(model=..., max_tokens=4096, messages=[...]) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()    # the full Message, with usage
```

## 6. Structured output with pydantic

```python
from pydantic import BaseModel

class Tags(BaseModel):
    tags: list[str]
    reason: str

response = client.messages.parse(model=..., max_tokens=1024, output_format=Tags, messages=[...])
response.parsed_output        # a validated Tags instance, not a string you have to parse
```

This is the reliable way to get data (not prose) out of an LLM.

## 7. Tool use (function calling)

You describe tools with a JSON schema. Claude decides when to call them, **your code runs them**, and you
send the results back. That loop is the core of every "agent":

```
you ──messages + tools──▶ Claude
     ◀── stop_reason="tool_use", content=[tool_use{id, name, input}]
you run the tool, then send:  assistant content + user [tool_result{tool_use_id, content}]
     ◀── stop_reason="end_turn", the final text answer
```

```python
tools = [{
    "name": "search_notes",
    "description": "Search the user's notes. Returns matching notes as JSON.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "Words to search for"}},
        "required": ["query"],
        "additionalProperties": False,
    },
    "strict": True,                    # guarantees the input matches the schema
}]
```

The SDK also has a **tool runner** that runs this loop for you: decorate functions with `@beta_tool`
and call `client.beta.messages.tool_runner(...)` (see the demo). In the exercise you'll write the loop by
hand once, so you understand what the runner does.

Tool-loop tips:
- Return errors as `{"type": "tool_result", ..., "is_error": True}`. Don't crash; Claude can recover.
- If one response has several `tool_use` blocks, send **all** their results back in **one** user message.
- Always cap the number of turns.

## 8. Async, errors, retries

```python
client = anthropic.AsyncAnthropic()
results = await asyncio.gather(*(client.messages.create(...) for note in notes))  # Lesson 12!
```

The SDK retries connection errors, 429 and 5xx automatically (`max_retries=2` by default). Catch specific
errors, most specific first: `anthropic.RateLimitError`, `anthropic.APIStatusError` (with `.status_code`),
and `anthropic.APIConnectionError`.

> Note: `anthropic` 1.x uses **`httpx2`** internally, not the `httpx` from Lesson 10. Same API, separate
> package. Don't pass `httpx` objects to the Anthropic client.

## 9. Testing LLM code

You don't want tests that cost money, are slow, and give different answers each run. **Inject the client** and
pass a fake one in tests: duck typing (Lesson 04) means any object with `.beta.messages.create(...)`
works. Test *your* logic (prompt construction, parsing, the tool loop, error handling), not the model.
To judge prompt quality, build a separate **eval** set: real inputs plus grading, run on purpose.

## 10. Run the example (needs an API key, and costs a few cents)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run python lessons/14_llm_claude/claude_demo.py
```

## 11. Exercise: the notes app gets a brain

Implement `exercise/llm_notes.py`: summaries, structured tag suggestions, streaming, a chat with
memory, and a hand-written tool loop that lets Claude search your notes. The tests use a fake client,
so **no API key is needed**.

```bash
uv run pytest lessons/14_llm_claude/exercise -v
```

Afterwards, try your functions for real with a key: `uv run python lessons/14_llm_claude/exercise/try_it.py`.
