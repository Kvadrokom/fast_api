from pydantic import BaseModel, PositiveInt
from typing import Union
from typing import Optional

class User(BaseModel):
    username: str
    password: str


class Todo(BaseModel):
    title: str | None = None
    description: str | None = None
    complited: bool = False


# Модель User для валидации входных данных
class UserCreate(BaseModel):
    username: str
    email: str


# Модель User для валидации исходящих данных - чисто для демонстрации (обычно входная модель шире чем выходная, т.к. на вход мы просим, например, пароль, который обратно не возвращаем, и другое, что не обязательно возвращать)
class UserReturn(BaseModel):
    username: str
    email: str
    id: Optional[int] = None

