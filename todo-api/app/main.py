from fastapi import FastAPI, HTTPException, status

from app.models import TodoCreate, TodoResponse, TodoUpdate
from app.store import TodoStore

app = FastAPI(title="Todo API", version="1.0.0")
store = TodoStore()


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate) -> TodoResponse:
    return store.create(todo)


@app.get("/todos", response_model=list[TodoResponse])
def list_todos() -> list[TodoResponse]:
    return store.list_all()


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int) -> TodoResponse:
    result = store.get(todo_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, updates: TodoUpdate) -> TodoResponse:
    result = store.update(todo_id, updates)
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int) -> None:
    if not store.delete(todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
