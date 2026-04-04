from datetime import datetime, timezone

from app.models import TodoCreate, TodoResponse, TodoUpdate


class TodoStore:
    def __init__(self) -> None:
        self._todos: dict[int, dict] = {}
        self._next_id: int = 1

    def create(self, todo: TodoCreate) -> TodoResponse:
        now = datetime.now(timezone.utc)
        record = {
            "id": self._next_id,
            "title": todo.title,
            "description": todo.description,
            "completed": False,
            "priority": todo.priority,
            "created_at": now,
            "updated_at": now,
        }
        self._todos[self._next_id] = record
        self._next_id += 1
        return TodoResponse(**record)

    def get(self, todo_id: int) -> TodoResponse | None:
        record = self._todos.get(todo_id)
        if record is None:
            return None
        return TodoResponse(**record)

    def list_all(self) -> list[TodoResponse]:
        return [TodoResponse(**r) for r in self._todos.values()]

    def update(self, todo_id: int, updates: TodoUpdate) -> TodoResponse | None:
        record = self._todos.get(todo_id)
        if record is None:
            return None
        patch = updates.model_dump(exclude_unset=True)
        if patch:
            record.update(patch)
            record["updated_at"] = datetime.now(timezone.utc)
        return TodoResponse(**record)

    def delete(self, todo_id: int) -> bool:
        return self._todos.pop(todo_id, None) is not None

    def clear(self) -> None:
        self._todos.clear()
        self._next_id = 1
