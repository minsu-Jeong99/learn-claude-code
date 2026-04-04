# Dividend Tracker App — Specification

## Overview
Django-based Dividend Tracker app with SQLite backend. Single-user, no authentication. Django templates (server-rendered HTML). Manual data entry only. Monthly dividend frequency focus.

---

## Project Location
`/Users/seungjoonlee/git/learn-claude-code/dividend_tracker/`

---

## Directory Structure
```
dividend_tracker/
    manage.py
    requirements.txt
    db.sqlite3                        # auto-created on migrate
    dividend_tracker/
        __init__.py
        settings.py
        urls.py
        wsgi.py
        asgi.py
    tracker/
        __init__.py
        models.py
        views.py
        forms.py
        urls.py
        admin.py
        apps.py
        templatetags/
            __init__.py
            tracker_filters.py
        migrations/
            __init__.py
    templates/
        base.html
        tracker/
            dashboard.html
            ticker_list.html
            ticker_detail.html
            ticker_form.html
            ticker_confirm_delete.html
            position_list.html
            position_detail.html
            position_form.html
            position_confirm_delete.html
            dividend_list.html
            dividend_form.html
            dividend_confirm_delete.html
            projection.html
    static/
        css/
            style.css
```

---

## Dependencies (`requirements.txt`)
```
Django>=5.1,<5.2
python-dateutil>=2.9
```

---

## Data Models (`tracker/models.py`)

### Ticker
| Field | Type | Notes |
|---|---|---|
| `symbol` | CharField(10, unique) | Uppercased on save |
| `name` | CharField(200) | Full name |
| `sector` | CharField(100, blank) | Optional |
| `current_price` | DecimalField(10,2, null) | Manual entry |
| `created_at` / `updated_at` | DateTimeField | auto |

**Properties:** `annual_dividend_per_share` (trailing 12-month sum, annualizes if < 12 months), `current_yield` (annual_div / current_price × 100)

### Position
| Field | Type | Notes |
|---|---|---|
| `ticker` | FK → Ticker | CASCADE |
| `shares` | DecimalField(12,4) | Fractional shares |
| `cost_basis_per_share` | DecimalField(10,2) | |
| `date_acquired` | DateField | |
| `notes` | TextField(blank) | |

**Properties:** `total_cost_basis`, `market_value`, `gain_loss`, `yield_on_cost`, `projected_monthly_income`, `projected_annual_income`

### Dividend
| Field | Type | Notes |
|---|---|---|
| `ticker` | FK → Ticker | CASCADE |
| `ex_date` | DateField | |
| `pay_date` | DateField(null) | Optional |
| `amount_per_share` | DecimalField(10,6) | |
| `unique_together` | (ticker, ex_date) | Prevents duplicates |

**Property:** `total_received` (amount × eligible position shares at ex_date)

---

## URL Structure

| URL | View | Purpose |
|---|---|---|
| `/` | `dashboard` | Summary dashboard |
| `/tickers/` | `ticker_list` | List tickers |
| `/tickers/add/` | `ticker_create` | Add ticker |
| `/tickers/<pk>/` | `ticker_detail` | Detail + dividends + positions |
| `/tickers/<pk>/edit/` | `ticker_update` | Edit ticker |
| `/tickers/<pk>/delete/` | `ticker_delete` | Delete confirm |
| `/positions/` | `position_list` | List positions |
| `/positions/add/` | `position_create` | Add position |
| `/positions/<pk>/` | `position_detail` | Position detail |
| `/positions/<pk>/edit/` | `position_update` | Edit |
| `/positions/<pk>/delete/` | `position_delete` | Delete confirm |
| `/dividends/` | `dividend_list` | List (filterable by ticker) |
| `/dividends/add/` | `dividend_create` | Add dividend record |
| `/dividends/<pk>/edit/` | `dividend_update` | Edit |
| `/dividends/<pk>/delete/` | `dividend_delete` | Delete confirm |
| `/projections/` | `projection` | 12-month income projection |

---

## Key Calculation Logic

### Monthly Income Projection
```
annual_div_per_share = sum of last 12 months of dividends
  → if < 12 months data: (sum / count) * 12
monthly_div_per_share = annual_div_per_share / 12
monthly_income = monthly_div_per_share * total_shares_across_positions
```

### Yield on Cost (per position)
```
(annual_div_per_share / cost_basis_per_share) * 100
```

### Current Yield (per ticker)
```
(annual_div_per_share / current_price) * 100
```

### Portfolio YOC (dashboard aggregate)
```
(total_annual_income / total_cost_basis) * 100
```

---

## Implementation Steps

1. **Scaffold project** — `django-admin startproject`, `startapp tracker`, configure `settings.py`
2. **Models + migrations** — write models, `makemigrations`, `migrate`, configure `admin.py`
3. **Forms** — `TickerForm`, `PositionForm`, `DividendForm` with CSS widget attrs
4. **URLs** — wire `tracker/urls.py` into project `urls.py`
5. **Ticker CRUD views + templates** — with `base.html`
6. **Position CRUD views + templates**
7. **Dividend CRUD views + templates**
8. **Dashboard view + template** — aggregate stats, recent dividends, top yielders
9. **Projection view + template** — 12-month forward table with per-ticker breakdown
10. **Template filters** — `currency`, `percentage`, `currency6` in `tracker_filters.py`
11. **CSS styling** — clean, minimal `style.css`

---

## Verification
1. `python manage.py check` — no errors
2. `python manage.py migrate` — clean migration
3. `python manage.py runserver` — visit `http://127.0.0.1:8000/`
4. Create a ticker (SCHD), add a position (100 shares @ $72), add 3 dividend records
5. Visit `/projections/` — confirm monthly income calculated correctly
6. Visit dashboard — confirm all aggregate stats render
7. `python manage.py test tracker` — all model/view/calculation tests pass
