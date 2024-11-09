from pydantic import BaseModel, PositiveInt
from typing import Union

class TodoReturn(BaseModel):
    title: str
    description: str
    completed: bool = False

class Todo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool = False
