# Dividend Tracker — User Manual

## Getting Started

### Prerequisites
- Python 3.10+
- `uv` (recommended) or `pip`

### Installation

```bash
cd dividend_tracker

# Create virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt

# Initialize the database
source .venv/bin/activate
python manage.py migrate

# (Optional) Create an admin superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Features Overview

| Feature | Description |
|---------|-------------|
| **Dashboard** | Portfolio summary — total cost basis, market value, monthly/annual income, portfolio yield on cost, top yielders, recent dividends |
| **Tickers** | Manage stock/ETF symbols with name, sector, and current price |
| **Positions** | Track shares held, cost basis, market value, gain/loss, and yield on cost |
| **Dividends** | Record dividend payments with ex-date, pay-date, and amount per share |
| **Projections** | 12-month forward income calendar with per-ticker breakdown |
| **Admin Panel** | Full Django admin interface for data management |

---

## Step-by-Step Usage

### 1. Add a Ticker
- Navigate to **Tickers** → **Add Ticker**
- Enter the stock symbol (e.g., `SCHD`), full name, sector (optional), and current price
- Click **Save**

### 2. Add a Position
- Navigate to **Positions** → **Add Position**
- Select the ticker, enter number of shares, cost basis per share, and date acquired
- Fractional shares are supported (up to 4 decimal places)
- Click **Save**

### 3. Record Dividends
- Navigate to **Dividends** → **Add Dividend**
- Select the ticker, enter the ex-dividend date, payment date (optional), and amount per share
- Amount supports up to 6 decimal places for precision
- Click **Save**

### 4. View Dashboard
- Visit the **Dashboard** (home page) to see:
  - Total cost basis and market value
  - Estimated monthly and annual income
  - Portfolio yield on cost
  - Top yielding positions
  - Recent dividend payments

### 5. View Income Projections
- Navigate to **Projections** to see:
  - Per-ticker breakdown: shares, annual dividend/share, monthly income, annual income
  - 12-month calendar showing projected total income per month

---

## URL Reference

| URL | Page |
|-----|------|
| `/` | Dashboard |
| `/tickers/` | Ticker list |
| `/tickers/add/` | Add ticker |
| `/tickers/<id>/` | Ticker detail (positions + dividend history) |
| `/tickers/<id>/edit/` | Edit ticker |
| `/tickers/<id>/delete/` | Delete ticker |
| `/positions/` | Position list |
| `/positions/add/` | Add position |
| `/positions/<id>/` | Position detail |
| `/positions/<id>/edit/` | Edit position |
| `/positions/<id>/delete/` | Delete position |
| `/dividends/` | Dividend list (filterable by ticker) |
| `/dividends/add/` | Add dividend |
| `/dividends/<id>/edit/` | Edit dividend |
| `/dividends/<id>/delete/` | Delete dividend |
| `/projections/` | 12-month income projection |
| `/admin/` | Django admin panel |

---

## How Calculations Work

### Annual Dividend per Share
- Sums all dividends with an ex-date within the trailing 12 months
- If fewer than 12 months of data exist: `(sum / count) x 12` (annualized estimate)

### Current Yield (per ticker)
```
current_yield = (annual_dividend_per_share / current_price) x 100
```

### Yield on Cost (per position)
```
yield_on_cost = (annual_dividend_per_share / cost_basis_per_share) x 100
```

### Monthly Income (per position)
```
monthly_income = (annual_dividend_per_share / 12) x shares
```

### Portfolio Yield on Cost (dashboard)
```
portfolio_yoc = (total_annual_income / total_cost_basis) x 100
```

---

## Data Models

### Ticker
| Field | Description |
|-------|-------------|
| Symbol | Stock/ETF ticker symbol (auto-uppercased) |
| Name | Full company or fund name |
| Sector | Optional sector classification |
| Current Price | Latest share price (manual entry) |

### Position
| Field | Description |
|-------|-------------|
| Ticker | Link to a ticker |
| Shares | Number of shares held (supports fractional) |
| Cost Basis/Share | Purchase price per share |
| Date Acquired | When the position was opened |
| Notes | Optional notes |

### Dividend
| Field | Description |
|-------|-------------|
| Ticker | Link to a ticker |
| Ex-Date | Ex-dividend date |
| Pay Date | Payment date (optional) |
| Amount/Share | Dividend amount per share |

---

## Tips

- **Filter dividends by ticker**: On the Dividends page, use the ticker filter dropdown to view dividends for a specific stock
- **Quick add from ticker detail**: When viewing a ticker's detail page, you can quickly add positions or dividends for that ticker
- **Update prices regularly**: Keep the "Current Price" field updated on tickers for accurate market value and current yield calculations
- **Admin panel**: Visit `/admin/` for bulk data management — search, filter, and edit records directly

---

## Technical Notes

- **Database**: SQLite (`db.sqlite3`) — created automatically on first migration
- **Framework**: Django 5.1
- **No authentication**: Single-user app, no login required
- **Static files**: Served via WhiteNoise in production
