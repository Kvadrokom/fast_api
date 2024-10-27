from pydantic import BaseModel, PositiveInt
from typing import Union

class User(BaseModel):
    username: str
    password: str


class Todo(BaseModel):
    title: str | None = None
    description: str | None = None
    complited: bool = False
