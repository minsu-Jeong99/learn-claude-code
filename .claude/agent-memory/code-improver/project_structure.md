---
name: project_structure
description: Repo layout, languages, frameworks, and recurring patterns found in learn-claude-code
type: project
---

Three independent sub-projects in one mono-repo:

1. **todo-api/** — FastAPI + Pydantic v2, in-memory store, pytest with TestClient. Well-structured.
2. **dividend_tracker/** — Django 5.1 app. Two settings files (app/settings.py for Vercel, dividend_tracker/settings.py for full app). Uses whitenoise, sqlite3 DB.
3. **mcp-server/** — Minimal FastMCP demo server.

Recurring patterns / anti-patterns identified:
- `dividend_tracker/tracker/tests.py` is empty — no Django-side tests at all.
- `app/settings.py` has `DEBUG = True` hardcoded and `ALLOWED_HOSTS = ['*']` — security risk.
- `dividend_tracker/settings.py` has a hardcoded insecure SECRET_KEY fallback.
- `TodoStore` uses a module-level singleton (`store = TodoStore()`) — shared state between test runs unless manually cleared; conftest calls `store.clear()` as a workaround.
- N+1 query risk: `Dividend.total_received` property iterates position_set in Python rather than using DB aggregation.
- `annual_dividend_per_share` property issues two separate DB queries when it could be one.
- `app/views.py` embeds a full HTML page as a raw string inside a Python function — should use a template.
- `api_data` has a hardcoded timestamp string `'2024-01-01T00:00:00Z'` — should be dynamic.
- `TodoStore._todos` typed as `dict[int, dict]` — the inner `dict` is untyped; should be `dict[int, TodoResponse]` or a TypedDict.
- `tracker_filters.py` converts Decimal to float for formatting — loses precision, should use Decimal formatting directly.
- `projection` view recomputes `ticker.position_set.all()` in a loop — already prefetched but still repeated evaluation.
- `conftest.py` clears store before test (not after) — if a test fails mid-suite the store may be dirty for the next; acceptable but worth noting.
