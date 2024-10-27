import psycopg2
from fastapi import FastAPI
from psycopg2.extras import DictCursor

from models import Todo

app = FastAPI()


def get_connection():
    connection = psycopg2.connect(dbname='api', user='postgres',
                        password=None, host='192.168.1.78')
    return connection


@app.post('/todos')
async def create_todo(data: Todo):
    conn = get_connection()
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('insert into stepic_api.todos(title, description, completed) values (%s, %s, %s)',
              (data.title, data.description, data.complited))
    conn.commit()
    c.execute('select * from stepic_api.todos where title = %s', (data.title, ))
    result = c.fetchone()
    c.close()
    conn.close()
    return {'id': result[0], 'title': result[1], 'description': result[2], 'complited': result[3]}


@app.get('/todos/{data_id}')
async def get_item(data_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute('select * from stepic_api.todos where id = %s', (data_id,))
    result = c.fetchone()
    c.close()
    conn.close()
    return {'id': result[0], 'title': result[1], 'description': result[2], 'complited': result[3]}


@app.put('/todos/update')
async def update_item(data: Todo):
    conn = get_connection()
    c = conn.cursor()
    c.execute('update stepic_api.todos set title = %s, description = %s, completed = %s',
              (data.title, data.description, data.complited))
    c.close()
    conn.close()
    return "Item update"


@app.delete('/todos/delete/{item_id}')
async def delete_item(item_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute('delete from stepic_api.todos where id = %s', (item_id,))
    c.close()
    conn.close()
    return "Item deleted"
