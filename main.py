from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from databases import Database
from models import UserReturn, UserCreate, UserUpdate

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

@app.put("/user/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    query = "UPDATE users SET username = :username, email = :email WHERE id = :user_id"
    values = user.model_dump(exclude_unset=True)
    query_dynamic_part = ", ".join([f"{key} = :{key}" for key in values.keys()])
    query = f"UPDATE stepic_api.users SET {query_dynamic_part} WHERE id = :user_id;"
    if not values:
        return {"message": "Empty data - nothing to update"}
    values["user_id"] = user_id
    try:
        await database.execute(query=query, values=values)
        return JSONResponse(content="", status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update user in database")


@app.delete("/user/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    query = "DELETE FROM stepic_api.users WHERE id = :user_id RETURNING id"
    values = {"user_id": user_id}
    try:
        deleted_rows = await database.execute(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete user from database")
    if deleted_rows:
        return {"message": "User  deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")