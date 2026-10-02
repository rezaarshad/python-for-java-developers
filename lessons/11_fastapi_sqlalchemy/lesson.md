# Lesson 11: REST APIs with FastAPI + SQLAlchemy

| Python        | Java/Spring equivalent                                         |
|---------------|-----------------------------------------------------------------|
| FastAPI       | Spring Web MVC (`@RestController`), plus springdoc OpenAPI for free |
| pydantic models | DTOs + Bean Validation                                       |
| `Depends(...)`| constructor injection / `@Autowired`                            |
| uvicorn       | embedded Tomcat/Netty (an ASGI server)                          |
| SQLAlchemy 2  | Hibernate/JPA (ORM) **and** jOOQ (SQL builder, "Core") in one   |
| Alembic       | Flyway/Liquibase (migrations)                                   |
| Django        | the "batteries included" alternative (≈ a full Spring Boot stack) |

## 1. FastAPI in 20 lines

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Notes")

class NoteIn(BaseModel):
    title: str

@app.get("/notes/{note_id}")                    # @GetMapping("/notes/{noteId}")
def get_note(note_id: int):                     # path param, parsed and validated as int
    if note_id not in db:
        raise HTTPException(status_code=404, detail="Note not found")
    return db[note_id]                          # dict or model → JSON automatically

@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(note: NoteIn, tag: str | None = None):   # pydantic param = JSON body; simple param = query string
    ...
```

Run it with `uv run uvicorn module:app --reload` and open **http://127.0.0.1:8000/docs** for an
interactive Swagger UI generated from your type hints. Bad input gets an automatic `422` with
pydantic's error details.

- `response_model=NoteOut` (or a return type annotation) filters and serializes the output: it never leaks fields that aren't in the model.
- `def` endpoints run in a thread pool; `async def` endpoints run on the event loop (Lesson 12).

## 2. Dependency injection with `Depends`

```python
def get_session():
    with Session(engine) as session:     # one session per request (≈ @Transactional request scope)
        yield session                    # teardown runs after the response is sent

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/notes")
def list_notes(session: SessionDep): ...
```

In tests, swap the dependency: `app.dependency_overrides[get_session] = get_test_session`.

## 3. SQLAlchemy 2.0 ORM

```python
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class Base(DeclarativeBase):
    pass

class NoteRow(Base):                            # @Entity
    __tablename__ = "notes"                     # @Table(name = "notes")
    id: Mapped[int] = mapped_column(primary_key=True)          # @Id @GeneratedValue
    title: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(default="")
    archived: Mapped[bool] = mapped_column(default=False)
    parent_id: Mapped[int | None]                               # nullable because of `| None`

engine = create_engine("sqlite:///notes.db", echo=True)        # echo=True logs SQL (≈ show_sql)
Base.metadata.create_all(engine)                               # ≈ ddl-auto=create (use Alembic in prod)

with Session(engine) as session:                               # ≈ EntityManager
    session.add(NoteRow(title="RAG"))
    session.commit()

    stmt = select(NoteRow).where(NoteRow.title.ilike("%rag%")).order_by(NoteRow.id)
    rows = session.scalars(stmt).all()                         # list[NoteRow]
    note = session.get(NoteRow, 1)                             # find by primary key, or None
    session.delete(note); session.commit()
```

Pydantic can read ORM objects directly: `model_config = ConfigDict(from_attributes=True)` then
`NoteOut.model_validate(row)`. FastAPI does this for you when the endpoint returns a row and declares a `response_model`.

## 4. Partial updates (PATCH)

```python
class NoteUpdate(BaseModel):
    title: str | None = None
    body: str | None = None

for field, value in update.model_dump(exclude_unset=True).items():  # only fields the client sent
    setattr(row, field, value)
```

## 5. Testing

```python
from fastapi.testclient import TestClient
client = TestClient(app)
r = client.post("/notes", json={"title": "RAG"})
assert r.status_code == 201
```

For a fresh database per test, use in-memory SQLite with `StaticPool`, so every connection sees the same DB.

## 6. Run the examples

```bash
uv run python lessons/11_fastapi_sqlalchemy/sqlalchemy_demo.py
uv run uvicorn --app-dir lessons/11_fastapi_sqlalchemy demo_api:app --reload
# → http://127.0.0.1:8000/docs
```

## 7. Exercise: the notes REST API

Implement `exercise/api_app.py`: the ORM model, the pydantic schemas, and CRUD endpoints. The database
plumbing is provided. It's the same API that your Lesson 10 client talks to.

```bash
uv run pytest lessons/11_fastapi_sqlalchemy/exercise -v
uv run uvicorn --app-dir lessons/11_fastapi_sqlalchemy/exercise api_app:app --reload   # try it at /docs
```
