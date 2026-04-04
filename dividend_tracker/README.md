# Dividend Tracker

A Django-based web app to track stock/ETF positions, dividend history, and project monthly income.

## Features

- **Tickers** — manage stock/ETF symbols with current price and sector
- **Positions** — track shares, cost basis, market value, gain/loss
- **Dividends** — log ex-dates, pay-dates, and per-share amounts
- **Dashboard** — portfolio summary with top yielders and recent dividends
- **Projections** — 12-month forward income calendar with per-ticker breakdown

## Setup

```bash
# 1. Create virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt

# 2. Run migrations
.venv/bin/python manage.py migrate

# 3. (Optional) Create admin user
.venv/bin/python manage.py createsuperuser

# 4. Start the server
.venv/bin/python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

## Quick Start

1. **Add a Ticker** — go to Tickers → Add Ticker, enter symbol (e.g. `SCHD`), full name, and current price
2. **Add a Position** — go to Positions → Add Position, select ticker, enter shares and cost basis per share
3. **Add Dividend Records** — go to Dividends → Add Dividend, enter ex-date and amount per share
4. **View Projections** — go to Projections to see monthly and annual income estimates

## URL Structure

| URL | Page |
|-----|------|
| `/` | Dashboard |
| `/tickers/` | Ticker list |
| `/tickers/add/` | Add ticker |
| `/tickers/<id>/` | Ticker detail + dividend history |
| `/positions/` | Position list |
| `/positions/add/` | Add position |
| `/positions/<id>/` | Position detail |
| `/dividends/` | Dividend log (filterable by ticker) |
| `/dividends/add/` | Add dividend record |
| `/projections/` | 12-month income projection |
| `/admin/` | Django admin |

## Calculations

**Annual Dividend per Share**
- Sum of dividends with ex-date in the trailing 12 months
- If data covers less than 12 months: `(sum / count) × 12` (annualized)

**Current Yield** = `annual_div_per_share / current_price × 100`

**Yield on Cost** = `annual_div_per_share / cost_basis_per_share × 100`

**Monthly Income** = `annual_div_per_share / 12 × total_shares`

**Portfolio YOC** = `total_annual_income / total_cost_basis × 100`

## Project Structure

```
dividend_tracker/
├── manage.py
├── requirements.txt
├── db.sqlite3                  # auto-created on migrate
├── dividend_tracker/
│   ├── settings.py
│   └── urls.py
├── tracker/
│   ├── models.py               # Ticker, Position, Dividend
│   ├── views.py                # 17 view functions
│   ├── forms.py                # ModelForms
│   ├── urls.py
│   ├── admin.py
│   └── templatetags/
│       └── tracker_filters.py  # currency, percentage filters
├── templates/
│   ├── base.html
│   └── tracker/                # 13 page templates
└── static/
    └── css/style.css
```

## Deploy to Vercel

### Prerequisites

- [Node.js](https://nodejs.org/) (for Vercel CLI)
- A [Vercel account](https://vercel.com/signup)

### Steps

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Navigate to the dividend_tracker directory
cd dividend_tracker

# 3. Deploy (first time will prompt to link/create a project)
vercel

# 4. (optional) Set environment variables
vercel env add DJANGO_SECRET_KEY production
# Enter a strong random string when prompted. Generate one with:
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

vercel env add DEBUG production
# Enter: False

# 5. If your repo has a Root Directory set in Vercel project settings, clear it
#    (Settings → General → Root Directory → leave empty → Save)

# 6. Deploy to production
vercel --prod
```

### Environment Variables

| Variable | Value | Required |
|----------|-------|----------|
| `DJANGO_SECRET_KEY` | A strong random string | Yes |
| `DEBUG` | `False` | Yes |

### What's already included (no action needed)

- `vercel.json` — routes and build config
- `build_files.sh` — installs deps and collects static files
- `whitenoise` in `requirements.txt` — serves static files in production
- `.gitignore` already excludes `.vercel/`, `.env.local`, and `db.sqlite3`

### What's account-specific (not committed to git)

- `.vercel/` — project link to your Vercel account (auto-created by `vercel` CLI)
- `.env.local` — local copy of env vars (auto-created by `vercel env pull`)

### Limitations

- Vercel serverless functions use an **ephemeral filesystem**, so the SQLite database will not persist between invocations. For production use, switch to a hosted database (e.g. Vercel Postgres, Neon, or Supabase).

## Notes

- Single-user, no authentication required
- SQLite database stored at `db.sqlite3`
- Fractional shares supported (4 decimal places)
- Dividend amounts stored to 6 decimal places
