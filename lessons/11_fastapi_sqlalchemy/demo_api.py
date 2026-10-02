"""Lesson 11 demo: a tiny in-memory FastAPI app.

Run:  uv run uvicorn --app-dir lessons/11_fastapi_sqlalchemy demo_api:app --reload
Then: http://127.0.0.1:8000/docs
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(title="Todo demo", version="1.0")


class TodoIn(BaseModel):
    title: str = Field(min_length=1, examples=["Learn FastAPI"])
    done: bool = False


class TodoOut(TodoIn):
    id: int


class TodoRepo:                           # a "service" bean
    def __init__(self) -> None:
        self.items: dict[int, TodoOut] = {}
        self.next_id = 1

    def add(self, todo: TodoIn) -> TodoOut:
        item = TodoOut(id=self.next_id, **todo.model_dump())
        self.items[item.id] = item
        self.next_id += 1
        return item


repo = TodoRepo()


def get_repo() -> TodoRepo:               # dependency provider (singleton here)
    return repo


RepoDep = Annotated[TodoRepo, Depends(get_repo)]


@app.get("/todos")
def list_todos(repo: RepoDep, done: bool | None = None,
               limit: Annotated[int, Query(ge=1, le=100)] = 10) -> list[TodoOut]:
    items = [t for t in repo.items.values() if done is None or t.done == done]
    return items[:limit]


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int, repo: RepoDep) -> TodoOut:
    if todo_id not in repo.items:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    return repo.items[todo_id]


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoIn, repo: RepoDep) -> TodoOut:
    return repo.add(todo)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, repo: RepoDep) -> None:
    if repo.items.pop(todo_id, None) is None:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
