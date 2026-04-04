import pytest


class TestCreateTodo:
    def test_create_minimal(self, client):
        resp = client.post("/todos", json={"title": "Buy milk"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Buy milk"
        assert data["description"] == ""
        assert data["completed"] is False
        assert data["priority"] == "medium"
        assert data["id"] == 1

    def test_create_full(self, client):
        resp = client.post(
            "/todos",
            json={
                "title": "Deploy app",
                "description": "Push to production",
                "priority": "high",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Deploy app"
        assert data["description"] == "Push to production"
        assert data["priority"] == "high"

    def test_create_empty_title_rejected(self, client):
        resp = client.post("/todos", json={"title": ""})
        assert resp.status_code == 422

    def test_create_missing_title_rejected(self, client):
        resp = client.post("/todos", json={})
        assert resp.status_code == 422

    def test_create_title_too_long(self, client):
        resp = client.post("/todos", json={"title": "x" * 201})
        assert resp.status_code == 422

    def test_create_invalid_priority(self, client):
        resp = client.post("/todos", json={"title": "Test", "priority": "urgent"})
        assert resp.status_code == 422

    def test_create_description_too_long(self, client):
        resp = client.post(
            "/todos", json={"title": "Test", "description": "x" * 1001}
        )
        assert resp.status_code == 422


class TestGetTodo:
    def test_get_existing(self, client):
        client.post("/todos", json={"title": "Item"})
        resp = client.get("/todos/1")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Item"

    def test_get_not_found(self, client):
        resp = client.get("/todos/999")
        assert resp.status_code == 404


class TestListTodos:
    def test_list_empty(self, client):
        resp = client.get("/todos")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_multiple(self, client):
        client.post("/todos", json={"title": "A"})
        client.post("/todos", json={"title": "B"})
        resp = client.get("/todos")
        assert len(resp.json()) == 2


class TestUpdateTodo:
    def test_update_title(self, client):
        client.post("/todos", json={"title": "Old"})
        resp = client.put("/todos/1", json={"title": "New"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New"

    def test_update_completed(self, client):
        client.post("/todos", json={"title": "Task"})
        resp = client.put("/todos/1", json={"completed": True})
        assert resp.status_code == 200
        assert resp.json()["completed"] is True

    def test_update_priority(self, client):
        client.post("/todos", json={"title": "Task"})
        resp = client.put("/todos/1", json={"priority": "high"})
        assert resp.status_code == 200
        assert resp.json()["priority"] == "high"

    def test_update_not_found(self, client):
        resp = client.put("/todos/999", json={"title": "Nope"})
        assert resp.status_code == 404

    def test_update_invalid_title(self, client):
        client.post("/todos", json={"title": "Task"})
        resp = client.put("/todos/1", json={"title": ""})
        assert resp.status_code == 422

    def test_update_preserves_unchanged_fields(self, client):
        client.post(
            "/todos",
            json={"title": "Task", "description": "Details", "priority": "low"},
        )
        resp = client.put("/todos/1", json={"completed": True})
        data = resp.json()
        assert data["title"] == "Task"
        assert data["description"] == "Details"
        assert data["priority"] == "low"
        assert data["completed"] is True


class TestDeleteTodo:
    def test_delete_existing(self, client):
        client.post("/todos", json={"title": "Delete me"})
        resp = client.delete("/todos/1")
        assert resp.status_code == 204
        # Verify it's gone
        resp = client.get("/todos/1")
        assert resp.status_code == 404

    def test_delete_not_found(self, client):
        resp = client.delete("/todos/999")
        assert resp.status_code == 404


class TestAutoIncrementId:
    def test_ids_increment(self, client):
        r1 = client.post("/todos", json={"title": "First"})
        r2 = client.post("/todos", json={"title": "Second"})
        assert r1.json()["id"] == 1
        assert r2.json()["id"] == 2
