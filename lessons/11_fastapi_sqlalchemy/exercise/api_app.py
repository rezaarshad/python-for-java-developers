"""Lesson 11 exercise: the notes REST API (FastAPI + SQLAlchemy + SQLite).

Run:   uv run uvicorn --app-dir lessons/11_fastapi_sqlalchemy/exercise api_app:app --reload
Test:  uv run pytest lessons/11_fastapi_sqlalchemy/exercise -v

Endpoints to build (the same API your Lesson 10 client calls):

    GET    /health              → 200 {"status": "ok"}                       (done, as an example)
    GET    /notes?tag=&q=       → 200 [NoteOut]   ordered by id; tag = exact tag match;
                                                  q = case-insensitive substring of title OR body
    (name the path parameter note_id: @app.get("/notes/{note_id}"))

    GET    /notes/{id}          → 200 NoteOut | 404 {"detail": "Note <id> not found"}
    POST   /notes               → 201 NoteOut     (body: NoteIn; invalid → 422 automatically)
    PATCH  /notes/{id}          → 200 NoteOut | 404   (body: NoteUpdate; only the fields that were sent change)
    DELETE /notes/{id}          → 204 | 404
"""

from collections.abc import Iterator
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import JSON, String, create_engine, or_, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


# --- Provided: database plumbing -------------------------------------------------------
class Base(DeclarativeBase):
    pass


engine = create_engine("sqlite:///notes.db", connect_args={"check_same_thread": False})


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# --- TODO: ORM model ---------------------------------------------------------------------
class NoteRow(Base):
    """Table "notes":
    - id: int primary key (done)
    - title: String(100)
    - body: str, default ""
    - tags: list[str] stored as JSON  (mapped_column(JSON, default=list))
    - created_at: datetime, default datetime.now (pass the function, don't call it!)
    """

    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)    # provided, so the module imports
    # TODO: the other four columns


# --- TODO: pydantic schemas -----------------------------------------------------------------
class NoteIn(BaseModel):
    """title: 1..100 chars, stripped; body: str = ""; tags: list[str] = [] (lowercased, deduped, ordered)."""
    # TODO (you wrote this in Lesson 10)


class NoteUpdate(BaseModel):
    """Every field optional (default None): title (1..100 chars), body, tags."""
    # TODO


class NoteOut(BaseModel):
    """id, title, body, tags, created_at. Needs model_config = ConfigDict(from_attributes=True)
    so it can be built from a NoteRow."""
    # TODO


# --- App ----------------------------------------------------------------------------------------
app = FastAPI(title="Notes API")
Base.metadata.create_all(engine)    # fine for learning; use Alembic migrations in real projects


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# TODO: a helper  get_row_or_404(session, note_id) -> NoteRow  that raises HTTPException(404, "Note <id> not found")

# TODO: the five /notes endpoints (see the module docstring)
