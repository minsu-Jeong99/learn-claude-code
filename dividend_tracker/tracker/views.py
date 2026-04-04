from decimal import Decimal
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Ticker, Position, Dividend
from .forms import TickerForm, PositionForm, DividendForm


# ── Dashboard ──────────────────────────────────────────────────────────────────

def dashboard(request):
    tickers = Ticker.objects.prefetch_related('position_set', 'dividend_set').all()
    positions = Position.objects.select_related('ticker').all()

    total_cost_basis = sum(p.total_cost_basis for p in positions)
    total_market_value = sum(p.market_value for p in positions if p.market_value is not None)
    total_annual_income = sum(p.projected_annual_income for p in positions)
    total_monthly_income = total_annual_income / 12 if total_annual_income else Decimal('0')

    portfolio_yoc = None
    if total_cost_basis:
        portfolio_yoc = (total_annual_income / total_cost_basis) * 100

    recent_dividends = Dividend.objects.select_related('ticker').order_by('-ex_date')[:10]

    top_yielders = sorted(
        [t for t in tickers if t.current_yield is not None],
        key=lambda t: t.current_yield,
        reverse=True
    )[:5]

    context = {
        'total_cost_basis': total_cost_basis,
        'total_market_value': total_market_value,
        'total_annual_income': total_annual_income,
        'total_monthly_income': total_monthly_income,
        'portfolio_yoc': portfolio_yoc,
        'recent_dividends': recent_dividends,
        'top_yielders': top_yielders,
        'positions': positions,
    }
    return render(request, 'tracker/dashboard.html', context)


# ── Ticker CRUD ────────────────────────────────────────────────────────────────

def ticker_list(request):
    tickers = Ticker.objects.prefetch_related('position_set', 'dividend_set').all()
    return render(request, 'tracker/ticker_list.html', {'tickers': tickers})


def ticker_detail(request, pk):
    ticker = get_object_or_404(Ticker, pk=pk)
    positions = ticker.position_set.all()
    dividends = ticker.dividend_set.order_by('-ex_date')
    context = {'ticker': ticker, 'positions': positions, 'dividends': dividends}
    return render(request, 'tracker/ticker_detail.html', context)


def ticker_create(request):
    if request.method == 'POST':
        form = TickerForm(request.POST)
        if form.is_valid():
            ticker = form.save()
            messages.success(request, f'Ticker {ticker.symbol} added.')
            return redirect('ticker_detail', pk=ticker.pk)
    else:
        form = TickerForm()
    return render(request, 'tracker/ticker_form.html', {'form': form, 'title': 'Add Ticker'})


def ticker_update(request, pk):
    ticker = get_object_or_404(Ticker, pk=pk)
    if request.method == 'POST':
        form = TickerForm(request.POST, instance=ticker)
        if form.is_valid():
            form.save()
            messages.success(request, f'Ticker {ticker.symbol} updated.')
            return redirect('ticker_detail', pk=ticker.pk)
    else:
        form = TickerForm(instance=ticker)
    return render(request, 'tracker/ticker_form.html', {'form': form, 'title': f'Edit {ticker.symbol}', 'ticker': ticker})


def ticker_delete(request, pk):
    ticker = get_object_or_404(Ticker, pk=pk)
    if request.method == 'POST':
        symbol = ticker.symbol
        ticker.delete()
        messages.success(request, f'Ticker {symbol} deleted.')
        return redirect('ticker_list')
    return render(request, 'tracker/ticker_confirm_delete.html', {'object': ticker, 'type': 'Ticker'})


# ── Position CRUD ──────────────────────────────────────────────────────────────

def position_list(request):
    positions = Position.objects.select_related('ticker').all()
    return render(request, 'tracker/position_list.html', {'positions': positions})


def position_detail(request, pk):
    position = get_object_or_404(Position, pk=pk)
    return render(request, 'tracker/position_detail.html', {'position': position})


def position_create(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            messages.success(request, f'Position added for {position.ticker.symbol}.')
            return redirect('position_detail', pk=position.pk)
    else:
        initial = {}
        ticker_pk = request.GET.get('ticker')
        if ticker_pk:
            initial['ticker'] = ticker_pk
        form = PositionForm(initial=initial)
    return render(request, 'tracker/position_form.html', {'form': form, 'title': 'Add Position'})


def position_update(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position updated.')
            return redirect('position_detail', pk=position.pk)
    else:
        form = PositionForm(instance=position)
    return render(request, 'tracker/position_form.html', {'form': form, 'title': 'Edit Position', 'position': position})


def position_delete(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        position.delete()
        messages.success(request, 'Position deleted.')
        return redirect('position_list')
    return render(request, 'tracker/position_confirm_delete.html', {'object': position, 'type': 'Position'})


# ── Dividend CRUD ──────────────────────────────────────────────────────────────

def dividend_list(request):
    dividends = Dividend.objects.select_related('ticker').order_by('-ex_date')
    ticker_filter = request.GET.get('ticker')
    if ticker_filter:
        dividends = dividends.filter(ticker__symbol__iexact=ticker_filter)
    tickers = Ticker.objects.all()
    context = {'dividends': dividends, 'tickers': tickers, 'ticker_filter': ticker_filter}
    return render(request, 'tracker/dividend_list.html', context)


def dividend_create(request):
    if request.method == 'POST':
        form = DividendForm(request.POST)
        if form.is_valid():
            dividend = form.save()
            messages.success(request, f'Dividend record added for {dividend.ticker.symbol}.')
            return redirect('dividend_list')
    else:
        initial = {}
        ticker_pk = request.GET.get('ticker')
        if ticker_pk:
            initial['ticker'] = ticker_pk
        form = DividendForm(initial=initial)
    return render(request, 'tracker/dividend_form.html', {'form': form, 'title': 'Add Dividend'})


def dividend_update(request, pk):
    dividend = get_object_or_404(Dividend, pk=pk)
    if request.method == 'POST':
        form = DividendForm(request.POST, instance=dividend)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dividend record updated.')
            return redirect('dividend_list')
    else:
        form = DividendForm(instance=dividend)
    return render(request, 'tracker/dividend_form.html', {'form': form, 'title': 'Edit Dividend', 'dividend': dividend})


def dividend_delete(request, pk):
    dividend = get_object_or_404(Dividend, pk=pk)
    if request.method == 'POST':
        dividend.delete()
        messages.success(request, 'Dividend record deleted.')
        return redirect('dividend_list')
    return render(request, 'tracker/dividend_confirm_delete.html', {'object': dividend, 'type': 'Dividend'})


# ── Projection ─────────────────────────────────────────────────────────────────

def projection(request):
    tickers = Ticker.objects.prefetch_related('position_set', 'dividend_set').all()

    rows = []
    total_monthly = Decimal('0')
    total_annual = Decimal('0')

    for ticker in tickers:
        total_shares = sum(p.shares for p in ticker.position_set.all())
        if not total_shares:
            continue
        annual_div = ticker.annual_dividend_per_share
        monthly_div = annual_div / 12
        monthly_income = monthly_div * total_shares
        annual_income = annual_div * total_shares

        total_monthly += monthly_income
        total_annual += annual_income

        rows.append({
            'ticker': ticker,
            'total_shares': total_shares,
            'annual_div_per_share': annual_div,
            'monthly_div_per_share': monthly_div,
            'monthly_income': monthly_income,
            'annual_income': annual_income,
        })

    rows.sort(key=lambda r: r['monthly_income'], reverse=True)

    # Build 12-month calendar
    today = date.today()
    monthly_calendar = []
    for i in range(12):
        month_offset = (today.month - 1 + i) % 12 + 1
        year_offset = today.year + (today.month - 1 + i) // 12
        monthly_calendar.append({
            'label': date(year_offset, month_offset, 1).strftime('%b %Y'),
            'income': total_monthly,
        })

    context = {
        'rows': rows,
        'total_monthly': total_monthly,
        'total_annual': total_annual,
        'monthly_calendar': monthly_calendar,
    }
    return render(request, 'tracker/projection.html', context)
