# Lesson 10: Validation with `pydantic` & HTTP with `httpx`

These two libraries are everywhere in modern Python, and **especially in AI code**: the Anthropic SDK
itself is built on pydantic + httpx, and FastAPI (next lesson) is built on pydantic.

| Library    | What it does                                           | Java analogue                          |
|------------|--------------------------------------------------------|----------------------------------------|
| `pydantic` | data classes that **validate and parse** at runtime    | Jackson + Bean Validation (`@NotNull`, `@Size`) |
| `httpx`    | HTTP client (sync **and** async)                       | `java.net.http.HttpClient`, OkHttp    |
| `requests` | the older, sync-only HTTP client you'll see in tutorials | Apache HttpClient                    |

## 1. Pydantic models

```python
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class Note(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=100)
    tags: list[str] = []                  # mutable defaults are safe here: pydantic copies them
    created_at: datetime

    @field_validator("tags")
    @classmethod
    def lowercase(cls, tags: list[str]) -> list[str]:
        return [t.lower() for t in tags]

note = Note(id="1", title="RAG", created_at="2026-10-02T12:00:00")   # coerced: "1" → 1, str → datetime
note.model_dump()                 # → dict          (≈ objectMapper.convertValue)
note.model_dump_json()            # → JSON string    (≈ writeValueAsString)
Note.model_validate({"id": 1, ...})       # dict → model
Note.model_validate_json('{"id": 1, ...}') # JSON → model (≈ readValue)
```

Invalid data raises a `ValidationError` that lists **every** problem, with its location:

```
1 validation error for Note
title
  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]
```

### Dataclass or pydantic?

- `@dataclass`: internal domain objects; no validation and no runtime cost.
- `pydantic.BaseModel`: **at the boundaries**: API requests/responses, config, files, LLM outputs.

Useful extras: `Literal["low", "high"]` (enum-like strings), `EmailStr`, `HttpUrl`, `model_config = ConfigDict(frozen=True)`,
`@computed_field`, `TypeAdapter(list[Note]).validate_python(data)` for non-model types, and the separate
`pydantic-settings` package for `.env`/environment config (≈ Spring `@ConfigurationProperties`).

## 2. httpx

```python
import httpx

r = httpx.get("https://api.example.com/notes", params={"tag": "ai"}, timeout=5.0)
r.status_code, r.json(), r.headers["content-type"]
r.raise_for_status()                       # raises httpx.HTTPStatusError for 4xx/5xx

# Reuse connections (always do this in real code), like a single shared HttpClient
with httpx.Client(base_url="https://api.example.com", headers={"Authorization": "Bearer ..."}, timeout=10) as client:
    notes = client.get("/notes").json()
    created = client.post("/notes", json={"title": "RAG"}).json()
```

Exceptions: `httpx.TimeoutException`, `httpx.ConnectError` (both subclasses of `httpx.RequestError`) and `httpx.HTTPStatusError`.

### Testing without a network: `MockTransport`

```python
def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/notes/1":
        return httpx.Response(200, json={"id": 1, "title": "RAG"})
    return httpx.Response(404)

client = httpx.Client(base_url="https://test", transport=httpx.MockTransport(handler))
```

Inject the transport and your code under test is unchanged. It's like WireMock, in-process.

## 3. Run the example

```bash
uv run python lessons/10_pydantic_httpx/demo.py      # parts of it call a public test API (needs internet)
```

## 4. Exercise: a typed client for a remote notes API

Implement `exercise/notes_client.py`:
- Pydantic models `NoteIn` (what you send) and `Note` (what you get back), with validation.
- `NotesClient`, a thin wrapper around `httpx.Client` that returns models, not dicts, and turns
  404s into a domain exception.

```bash
uv run pytest lessons/10_pydantic_httpx/exercise -v
```
