# Todo API

A REST API for managing todos, built with FastAPI and Pydantic.

## Setup

```bash
cd todo-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API Endpoints

### Create a todo

```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "description": "From the store", "priority": "high"}'
```

Only `title` is required. `priority` defaults to `"medium"`. Valid priorities: `low`, `medium`, `high`.

### List all todos

```bash
curl http://localhost:8000/todos
```

### Get a single todo

```bash
curl http://localhost:8000/todos/1
```

### Update a todo

```bash
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

All fields are optional. Only provided fields are updated.

### Delete a todo

```bash
curl -X DELETE http://localhost:8000/todos/1
```

## Validation Rules

| Field | Constraint |
|-------|-----------|
| `title` | Required, 1-200 characters |
| `description` | Optional, max 1000 characters |
| `priority` | `low`, `medium`, or `high` |

Invalid input returns `422` with error details. Missing resources return `404`.

## Run tests

```bash
pytest tests/ -v
```
