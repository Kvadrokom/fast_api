from fastapi import FastAPI, HTTPException
from databases import Database
from models import UserReturn, UserCreate
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# URL для PostgreSQL (измените его под свою БД)
DATABASE_URL = "postgresql://postgres@192.168.1.78/api"

database = Database(DATABASE_URL)

# тут устанавливаем условия подключения к базе данных и отключения - можно использовать в роутах контекстный менеджер async with Database(...) as db: etc
@app.on_event("startup")
async def startup_database():
    await database.connect()


@app.on_event("shutdown")
async def shutdown_database():
    await database.disconnect()


# создание роута для создания юзеров
@app.post("/users/", response_model=UserReturn)
async def create_user(user: UserCreate):
    query = "INSERT INTO stepic_api.users (username, email) VALUES (:username, :email) RETURNING id"
    values = {"username": user.username, "email": user.email}
    try:
        user_id = await database.execute(query=query, values=values)
        return {**user.dict(), "id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.get("/user/{user_id}", response_model=UserReturn)
async def get_user(user_id: int):
    query = "SELECT * FROM stepic_api.users WHERE id = :user_id"
    values = {"user_id": user_id}
    try:
        result = await database.fetch_one(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch user from database")
    if result:
        return UserReturn(username=result["username"], email=result["email"], id=user_id)
    else:
        raise HTTPException(status_code=404, detail="User not found")

