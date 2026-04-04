# Django → FastAPI Migration Spec

## Context

Migrate the existing Django 5.1 dividend tracker to FastAPI with SQLAlchemy + Jinja2. The app is a server-rendered HTML application (not a REST API). Single user, no auth, SQLite database.

---

## Target Directory Structure

```
dividend_tracker/
    app/
        __init__.py
        main.py                 # FastAPI app, Jinja2 env, static files, router mounts
        config.py               # Settings (DB path, debug)
        database.py             # SQLAlchemy engine, SessionLocal, Base
        models.py               # SQLAlchemy ORM models (Ticker, Position, Dividend)
        schemas.py              # Pydantic models for form validation
        dependencies.py         # Deps: get_db, get_templates, flash messages
        template_filters.py     # Jinja2 custom filters (currency, percentage, etc.)
        routers/
            __init__.py
            tickers.py          # Ticker CRUD routes
            positions.py        # Position CRUD routes
            dividends.py        # Dividend CRUD routes
            dashboard.py        # Dashboard + projection routes
    templates/                  # Adapted from Django to Jinja2 syntax
        base.html
        tracker/
            (same 13 templates, converted)
    static/
        css/style.css           # Unchanged
    requirements.txt            # Updated for FastAPI stack
    db.sqlite3                  # Unchanged (compatible schema)
    specs/                      # Unchanged
```

Old Django files to remove after migration: `manage.py`, `dividend_tracker/` (settings pkg), `tracker/` (django app).

---

## Dependencies (`requirements.txt`)

```
fastapi>=0.115
uvicorn[standard]>=0.34
sqlalchemy>=2.0
jinja2>=3.1
python-multipart>=0.0.9
python-dateutil>=2.9
itsdangerous>=2.2
```

- `python-multipart` — required for `Form(...)` parameters
- `itsdangerous` — session cookie signing for flash messages

---

## Database Layer

### `app/config.py`

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
SECRET_KEY = "dev-secret-key-change-in-production"
```

### `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass
```

---

## SQLAlchemy Models (`app/models.py`)

Map from Django ORM. Computed properties become regular Python methods/properties on the model classes.

### Ticker

```python
class Ticker(Base):
    __tablename__ = "tracker_ticker"   # Keep existing table name

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    sector = Column(String(100), default="")
    current_price = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    positions = relationship("Position", back_populates="ticker", cascade="all, delete-orphan")
    dividends = relationship("Dividend", back_populates="ticker", cascade="all, delete-orphan")
```

Properties: `annual_dividend_per_share`, `current_yield` — same logic as Django, using `self.dividends` instead of `self.dividend_set`.

### Position

```python
class Position(Base):
    __tablename__ = "tracker_position"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tracker_ticker.id", ondelete="CASCADE"), nullable=False)
    shares = Column(Numeric(12, 4), nullable=False)
    cost_basis_per_share = Column(Numeric(10, 2), nullable=False)
    date_acquired = Column(Date, nullable=False)
    notes = Column(Text, default="")

    ticker = relationship("Ticker", back_populates="positions")
```

Properties: `total_cost_basis`, `market_value`, `gain_loss`, `yield_on_cost`, `projected_annual_income`, `projected_monthly_income` — same logic.

### Dividend

```python
class Dividend(Base):
    __tablename__ = "tracker_dividend"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tracker_ticker.id", ondelete="CASCADE"), nullable=False)
    ex_date = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=True)
    amount_per_share = Column(Numeric(10, 6), nullable=False)

    ticker = relationship("Ticker", back_populates="dividends")

    __table_args__ = (UniqueConstraint("ticker_id", "ex_date"),)
```

Property: `total_received` — same logic, using `self.ticker.positions` with filter.

---

## Pydantic Schemas (`app/schemas.py`)

Used for form validation. Not for API serialization (this is server-rendered).

```python
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date
from decimal import Decimal

class TickerCreate(BaseModel):
    symbol: str
    name: str
    sector: str = ""
    current_price: Optional[Decimal] = None

    @field_validator("symbol")
    @classmethod
    def uppercase_symbol(cls, v):
        return v.strip().upper()

class PositionCreate(BaseModel):
    ticker_id: int
    shares: Decimal
    cost_basis_per_share: Decimal
    date_acquired: date
    notes: str = ""

class DividendCreate(BaseModel):
    ticker_id: int
    ex_date: date
    pay_date: Optional[date] = None
    amount_per_share: Decimal
```

---

## Dependencies (`app/dependencies.py`)

```python
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Flash Messages

Use Starlette's `SessionMiddleware` + helpers:

```python
from starlette.requests import Request

def flash(request: Request, message: str, category: str = "success"):
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})

def get_flashed_messages(request: Request):
    messages = request.session.pop("_messages", [])
    return messages
```

---

## Main App (`app/main.py`)

```python
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.config import BASE_DIR, SECRET_KEY
from app.database import engine, Base
from app.template_filters import register_filters
from app.dependencies import get_flashed_messages

app = FastAPI(title="Dividend Tracker")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")
register_filters(templates.env)

# Make get_flashed_messages available in all templates
@app.middleware("http")
async def inject_messages(request: Request, call_next):
    response = await call_next(request)
    return response

# Create tables (idempotent — existing tables are not touched)
Base.metadata.create_all(bind=engine)

# Import routers
try:
    from app.routers import tickers
    app.include_router(tickers.router)
except ImportError:
    pass
try:
    from app.routers import positions
    app.include_router(positions.router)
except ImportError:
    pass
try:
    from app.routers import dividends
    app.include_router(dividends.router)
except ImportError:
    pass
try:
    from app.routers import dashboard
    app.include_router(dashboard.router)
except ImportError:
    pass
```

Run with: `uvicorn app.main:app --reload`

---

## Custom Template Filters (`app/template_filters.py`)

Register on the Jinja2 `Environment`:

```python
def register_filters(env):
    env.filters["currency"] = currency
    env.filters["currency6"] = currency6
    env.filters["percentage"] = percentage
    env.filters["abs_value"] = abs_value
    env.filters["gain_loss_class"] = gain_loss_class
```

Same logic as `tracker/templatetags/tracker_filters.py`.

---

## Template Conversion (Django → Jinja2)

### Syntax changes applied to ALL templates:

| Django | Jinja2 (FastAPI) |
|--------|-----------------|
| `{% load static %}` | Remove (static files use `url_for`) |
| `{% load tracker_filters %}` | Remove (filters registered globally) |
| `{% static 'css/style.css' %}` | `{{ url_for('static', path='css/style.css') }}` |
| `{% url 'name' %}` | `{{ url_for('name') }}` |
| `{% url 'name' obj.pk %}` | `{{ url_for('name', pk=obj.id) }}` |
| `{% csrf_token %}` | Remove (not needed for single-user app) |
| `{% empty %}` (in for loops) | `{% else %}` |
| `{{ value\|default:"—" }}` | `{{ value or "—" }}` |
| `request.resolver_match.url_name` | `active_page` (passed in context) |
| `{% if messages %}` (Django messages) | `{% if messages %}` (from `get_flashed_messages()`) |
| `{{ message.tags == 'error' }}` | `{{ m.category == 'error' }}` |
| `{{ field.id_for_label }}` | Manual `id` attributes |
| `{{ field }}` (Django form widget) | Manual `<input>` HTML |
| `{{ field.label }}` | Manual `<label>` text |
| `{{ field.errors.as_text }}` | `{{ errors.field_name }}` (passed from route) |

### Form template pattern (replaces Django auto-rendered forms):

```html
<div class="form-group">
  <label for="symbol">Symbol</label>
  <input type="text" id="symbol" name="symbol" class="form-control"
         placeholder="e.g. SCHD" value="{{ form_data.symbol or '' }}" required>
  {% if errors.symbol %}
  <div style="color:var(--negative);font-size:12px;margin-top:4px">{{ errors.symbol }}</div>
  {% endif %}
</div>
```

Routes pass `form_data` (dict of current values) and `errors` (dict of field→message) to templates on validation failure.

### base.html navigation (active page detection):

Routes pass `active_page` in template context. The base template checks:
```html
<a href="{{ url_for('dashboard') }}" {% if active_page == 'dashboard' %}class="active"{% endif %}>Dashboard</a>
<a href="{{ url_for('ticker_list') }}" {% if active_page == 'tickers' %}class="active"{% endif %}>Tickers</a>
```

---

## Router Patterns

### List route example:

```python
@router.get("/tickers/", name="ticker_list")
async def ticker_list(request: Request, db: Session = Depends(get_db)):
    tickers = db.query(Ticker).order_by(Ticker.symbol).all()
    messages = get_flashed_messages(request)
    return templates.TemplateResponse(request, "tracker/ticker_list.html", {
        "tickers": tickers,
        "messages": messages,
        "active_page": "tickers",
    })
```

### Create route example (GET + POST):

```python
@router.get("/tickers/add/", name="ticker_create")
async def ticker_create_form(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "tracker/ticker_form.html", {
        "title": "Add Ticker",
        "form_data": {},
        "errors": {},
        "active_page": "tickers",
    })

@router.post("/tickers/add/")
async def ticker_create(
    request: Request,
    db: Session = Depends(get_db),
    symbol: str = Form(...),
    name: str = Form(...),
    sector: str = Form(""),
    current_price: Optional[float] = Form(None),
):
    # Validate
    errors = {}
    if not symbol.strip():
        errors["symbol"] = "Symbol is required"
    # ... more validation ...
    if errors:
        return templates.TemplateResponse(request, "tracker/ticker_form.html", {
            "title": "Add Ticker",
            "form_data": {"symbol": symbol, "name": name, "sector": sector, "current_price": current_price},
            "errors": errors,
            "active_page": "tickers",
        })
    ticker = Ticker(symbol=symbol.upper(), name=name, sector=sector, current_price=current_price)
    db.add(ticker)
    db.commit()
    db.refresh(ticker)
    flash(request, f"Ticker {ticker.symbol} added.")
    return RedirectResponse(url=request.url_for("ticker_detail", pk=ticker.id), status_code=303)
```

### Delete route example:

```python
@router.get("/tickers/{pk}/delete/", name="ticker_delete")
async def ticker_delete_confirm(request: Request, pk: int, db: Session = Depends(get_db)):
    ticker = db.get(Ticker, pk)
    if not ticker:
        raise HTTPException(404)
    return templates.TemplateResponse(request, "tracker/ticker_confirm_delete.html", {
        "object": ticker, "type": "Ticker", "active_page": "tickers",
    })

@router.post("/tickers/{pk}/delete/")
async def ticker_delete(request: Request, pk: int, db: Session = Depends(get_db)):
    ticker = db.get(Ticker, pk)
    if not ticker:
        raise HTTPException(404)
    symbol = ticker.symbol
    db.delete(ticker)
    db.commit()
    flash(request, f"Ticker {symbol} deleted.")
    return RedirectResponse(url=request.url_for("ticker_list"), status_code=303)
```

**Important:** POST redirects MUST use `status_code=303` (See Other) so the browser issues a GET to the redirect target.

---

## URL Mapping (Django → FastAPI)

All URL patterns preserved. Route names preserved for `url_for()` compatibility.

| URL | Route Name | Router File |
|-----|-----------|-------------|
| `/` | `dashboard` | `dashboard.py` |
| `/tickers/` | `ticker_list` | `tickers.py` |
| `/tickers/add/` | `ticker_create` | `tickers.py` |
| `/tickers/{pk}/` | `ticker_detail` | `tickers.py` |
| `/tickers/{pk}/edit/` | `ticker_update` | `tickers.py` |
| `/tickers/{pk}/delete/` | `ticker_delete` | `tickers.py` |
| `/positions/` | `position_list` | `positions.py` |
| `/positions/add/` | `position_create` | `positions.py` |
| `/positions/{pk}/` | `position_detail` | `positions.py` |
| `/positions/{pk}/edit/` | `position_update` | `positions.py` |
| `/positions/{pk}/delete/` | `position_delete` | `positions.py` |
| `/dividends/` | `dividend_list` | `dividends.py` |
| `/dividends/add/` | `dividend_create` | `dividends.py` |
| `/dividends/{pk}/edit/` | `dividend_update` | `dividends.py` |
| `/dividends/{pk}/delete/` | `dividend_delete` | `dividends.py` |
| `/projections/` | `projection` | `dashboard.py` |

---

## Work Unit Decomposition (5 parallel units)

Each worker creates the full shared infrastructure (identical files) plus their unique domain files. Shared files merge cleanly across PRs since content is identical.

### Unit 1: Core Infrastructure + Base Template

**Creates:**
- `app/__init__.py`
- `app/main.py`
- `app/config.py`
- `app/database.py`
- `app/models.py`
- `app/schemas.py`
- `app/dependencies.py`
- `app/template_filters.py`
- `app/routers/__init__.py`

**Modifies:**
- `requirements.txt`
- `templates/base.html` (Django → Jinja2)

**Does NOT create any routers.** Tests by running `uvicorn app.main:app` and verifying the server starts without errors.

### Unit 2: Ticker CRUD

**Creates (shared infra, identical to Unit 1):** all `app/*.py` and `app/routers/__init__.py` files
**Creates (unique):** `app/routers/tickers.py`
**Modifies:**
- `templates/tracker/ticker_list.html`
- `templates/tracker/ticker_detail.html`
- `templates/tracker/ticker_form.html` (rewrite with manual HTML form)
- `templates/tracker/ticker_confirm_delete.html`

### Unit 3: Position CRUD

**Creates (shared infra):** same
**Creates (unique):** `app/routers/positions.py`
**Modifies:**
- `templates/tracker/position_list.html`
- `templates/tracker/position_detail.html`
- `templates/tracker/position_form.html` (rewrite with manual HTML form + ticker dropdown)
- `templates/tracker/position_confirm_delete.html`

### Unit 4: Dividend CRUD

**Creates (shared infra):** same
**Creates (unique):** `app/routers/dividends.py`
**Modifies:**
- `templates/tracker/dividend_list.html`
- `templates/tracker/dividend_form.html` (rewrite with manual HTML form + ticker dropdown)
- `templates/tracker/dividend_confirm_delete.html`

### Unit 5: Dashboard & Projections

**Creates (shared infra):** same
**Creates (unique):** `app/routers/dashboard.py`
**Modifies:**
- `templates/tracker/dashboard.html`
- `templates/tracker/projection.html`

---

## E2E Test Recipe

Each worker verifies their changes by:

1. Install deps: `pip install -r requirements.txt`
2. Start server: `uvicorn app.main:app --host 127.0.0.1 --port 8000 &`
3. Wait for startup: `sleep 2`
4. Curl their routes and check for 200 + expected content:
   - Unit 1: `curl -s http://127.0.0.1:8000/` (should get 404 or empty, since no dashboard router)
   - Unit 2: `curl -s http://127.0.0.1:8000/tickers/` (should get 200 with "Tickers" heading)
   - Unit 3: `curl -s http://127.0.0.1:8000/positions/` (200 with "Positions")
   - Unit 4: `curl -s http://127.0.0.1:8000/dividends/` (200 with "Dividends")
   - Unit 5: `curl -s http://127.0.0.1:8000/` (200 with "Portfolio Dashboard")
5. Test create flow: POST a form, follow redirect, verify item appears
6. Kill server: `kill %1`

---

## Verification (post-merge)

1. `pip install -r requirements.txt`
2. `uvicorn app.main:app --reload`
3. Visit `http://127.0.0.1:8000/` — dashboard loads
4. Create a ticker (SCHD), add a position (100 shares @ $72), add 3 dividend records
5. Visit `/projections/` — monthly income calculated
6. Visit `/tickers/` — all tickers with yields
7. Edit and delete operations work
8. Flash messages appear after operations
9. All pages render without template errors
10. Remove old Django files: `manage.py`, `dividend_tracker/`, `tracker/`
