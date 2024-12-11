from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from databases import Database
from models import TodoCreate, TodoReturn, TodoUpdate, Todo

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


# создание роута для создания item_todo
@app.post("/todos", response_model=Todo)
async def create_item(item: TodoCreate):
    query = "INSERT INTO stepic_api.todos (title, description, completed) VALUES (:title, \
            :description, :completed) RETURNING id"
    values = {"title": item.title, "description": item.description, "completed": False}
    try:
        item_id = await database.execute(query=query, values=values)
        return {**item.dict(), "id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.get("/todos/{item_id}", response_model=TodoReturn)
async def get_user(item_id: int):
    query = "SELECT * FROM stepic_api.todos WHERE id = :item_id"
    values = {"item_id": item_id}
    try:
        result = await database.fetch_one(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch todo_item from database")
    if result:
        print(result)
        return TodoReturn(title=result["title"], description=result["description"],
                          completed=result["completed"])
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.put("/todos/{item_id}")
async def update_user(item_id: int, todo: TodoUpdate):
    values = todo.model_dump(exclude_unset=True)
    query_dynamic_part = ", ".join([f"{key} = :{key}" for key in values.keys()])
    query = f"UPDATE stepic_api.todos SET {query_dynamic_part} WHERE id = :item_id;"
    if not values:
        return {"message": "Empty data - nothing to update"}
    values["item_id"] = item_id
    try:
        await database.execute(query=query, values=values)
        return {**values}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update user in database")


@app.delete("/todos/{item_id}", response_model=dict)
async def delete_user(item_id: int):
    query = "DELETE FROM stepic_api.todos WHERE id = :item_id RETURNING id"
    values = {"item_id": item_id}
    try:
        deleted_rows = await database.execute(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete user from database")
    if deleted_rows:
        return {"message": "Item  deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")