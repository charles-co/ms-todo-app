import requests

from src.config.settings import get_settings
from src.db import DynamoDB
from tests.factories import TodoDBSchemaFactory

settings = get_settings()
dynamodb = DynamoDB(table_name=settings.TODO_APP_DB)
BASE_URL = "http://localhost:3000"


def test_get_todo(server, clear_db):
    # Create a todo
    path = "/test/todos/{id}"
    todo = TodoDBSchemaFactory.build()
    dynamodb.put_item(todo.model_dump())

    resp = requests.get(BASE_URL + path.format(id=todo.id))
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == todo.id


def test_get_todos(server, clear_db):
    # Create todos
    path = "/test/todos"
    size = 20
    todos = TodoDBSchemaFactory.batch(size)

    for todo in todos:
        dynamodb.put_item(todo.model_dump())

    resp = requests.get(BASE_URL + path)
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == size


def test_delete_todos(server, clear_db):
    # Create a todo
    path = "/test/todos/{id}"
    todo = TodoDBSchemaFactory.build()
    dynamodb.put_item(todo.model_dump())

    resp = requests.delete(BASE_URL + path.format(id=todo.id))
    assert resp.status_code == 204
    assert len(dynamodb.scan()["Items"]) == 0
